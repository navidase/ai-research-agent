import json
import ollama

from search import search
from memory import save_memory, search_memory
from rag import search_index
from tools import calculator


MODEL_NAME = "qwen2.5:1.5b"


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are an AI Research Agent.

You have access to these tools:
- web search
- calculator
- persistent memory
- local RAG knowledge base

Rules:

1. Use web search for current, recent, latest, news, research,
   or information that may have changed.

2. When web search returns results, USE those results.
   Do not claim that no results were found if results were returned.

3. When answering from web search results:
   - summarize the useful information
   - do not invent facts
   - include relevant source URLs

4. Use memory when the user asks about information they previously
   told you about themselves.

5. Save stable personal facts and preferences when appropriate.

6. Use the calculator for arithmetic instead of calculating manually
   when a calculation tool is appropriate.

7. Use the RAG tool when the question is about the local knowledge base.

8. Be concise, accurate, and useful.
"""


# =========================================================
# WEB SEARCH
# =========================================================

def search_web(query):
    results = search(query)

    if not results:
        return "No search results found."

    formatted_results = []

    for result in results[:5]:
        title = result.get("title", "No title")
        url = result.get("url", "")
        content = result.get("content", "")

        # Keep local LLM context reasonably small
        content = content[:1000]

        formatted_results.append(
            f"TITLE: {title}\n"
            f"URL: {url}\n"
            f"CONTENT: {content}"
        )

    return "\n\n".join(formatted_results)


# =========================================================
# QUESTION ROUTING
# =========================================================

def is_math_question(question):
    cleaned = question.replace(" ", "")

    if not cleaned:
        return False

    math_chars = "0123456789+-*/().%"

    return (
        any(char.isdigit() for char in cleaned)
        and all(char in math_chars for char in cleaned)
    )


def is_rag_question(question):
    q = question.lower().strip()

    keywords = [
        "knowledge base",
        "knowledge",
        "document",
        "local document",
        "according to",
        "according to the knowledge",
        "what is navid learning",
        "what does navid learn",
    ]

    return any(keyword in q for keyword in keywords)


def is_explicit_web_search(question):
    q = question.lower().strip()

    keywords = [
        "search the web",
        "search web",
        "web search",
        "search online",
        "look up",
        "latest",
        "recent news",
        "latest news",
        "current news",
        "today's news",
        "news about",
    ]

    return any(keyword in q for keyword in keywords)


# =========================================================
# PERSONAL MEMORY HELPERS
# =========================================================

def should_save_personal_memory(question):
    q = question.lower().strip()

    # Examples:
    # My favorite programming language is Python.
    # My favorite framework is FastAPI.
    if q.startswith("my ") and " is " in q:
        return True

    # Examples:
    # I live in Tehran.
    # I work as ...
    # I prefer Python.
    # I like machine learning.
    prefixes = [
        "i live in ",
        "i work ",
        "i prefer ",
        "i like ",
        "i love ",
        "my name is ",
    ]

    return any(q.startswith(prefix) for prefix in prefixes)


def extract_memory_query(question):
    q = question.lower().strip()

    prefixes = [
        "what is my ",
        "what's my ",
        "do you remember my ",
    ]

    for prefix in prefixes:
        if q.startswith(prefix):
            query = q[len(prefix):]
            return query.rstrip(" ?.")

    return None


# =========================================================
# TOOL DEFINITIONS
# =========================================================

tools = [

    # -----------------------------------------------------
    # RAG SEARCH
    # -----------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "rag_search",
            "description": (
                "Search the local knowledge base. "
                "Use this when the user asks about information "
                "contained in local documents or stored knowledge."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Information to search for in the "
                            "local knowledge base."
                        ),
                    }
                },
                "required": ["query"],
            },
        },
    },

    # -----------------------------------------------------
    # MEMORY SEARCH
    # -----------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "memory_search",
            "description": (
                "Search persistent memory for personal information "
                "previously provided by the user."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Personal information to search for."
                        ),
                    }
                },
                "required": ["query"],
            },
        },
    },

    # -----------------------------------------------------
    # MEMORY SAVE
    # -----------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "memory_save",
            "description": (
                "Save important stable personal information, "
                "preferences, goals, location, job, or other "
                "facts for future conversations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": (
                            "Personal information that should be saved."
                        ),
                    }
                },
                "required": ["content"],
            },
        },
    },

    # -----------------------------------------------------
    # CALCULATOR
    # -----------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": (
                "Safely calculate mathematical and arithmetic "
                "expressions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "A mathematical expression such as "
                            "(25 * 8) + 17."
                        ),
                    }
                },
                "required": ["expression"],
            },
        },
    },

    # -----------------------------------------------------
    # WEB SEARCH
    # -----------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": (
                "Search the web for current, latest, recent, "
                "news, research, or other up-to-date information."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search on the web.",
                    }
                },
                "required": ["query"],
            },
        },
    },
]


# =========================================================
# TOOL ARGUMENT HELPER
# =========================================================

def normalize_arguments(arguments):
    """
    Ollama versions may return tool arguments either as
    a dictionary or JSON string.
    """

    if isinstance(arguments, dict):
        return arguments

    if isinstance(arguments, str):
        try:
            return json.loads(arguments)
        except json.JSONDecodeError:
            return {}

    return {}


# =========================================================
# RAG ANSWER
# =========================================================

def answer_with_rag(question):
    print("TOOL: rag_search")

    results = search_index(question)

    if not results:
        result = "No relevant information found."
    else:
        result = "\n\n".join(results)

    print("TOOL RESULT:")
    print(result)

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer the user's question using ONLY the "
                    "provided local knowledge base context. "
                    "If the answer is not present, say that you "
                    "do not have enough information. "
                    "Do not invent facts."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question:\n{question}\n\n"
                    f"Knowledge base context:\n{result}"
                ),
            },
        ],
    )

    return response.message.content


# =========================================================
# WEB SEARCH ANSWER
# =========================================================

def answer_with_web_search(question):
    print("TOOL: search_web")

    result = search_web(question)

    print("TOOL RESULT:")
    print(result)

    if result == "No search results found.":
        return result

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a research assistant. "
                    "Answer using the web search results provided. "
                    "Do NOT say that you cannot access the web. "
                    "Do NOT say that no results were found because "
                    "results have already been provided. "
                    "Summarize the most relevant information. "
                    "Include source URLs from the search results. "
                    "Do not invent facts."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"User question:\n{question}\n\n"
                    f"WEB SEARCH RESULTS:\n{result}"
                ),
            },
        ],
    )

    return response.message.content


# =========================================================
# MAIN AGENT LOOP
# =========================================================

print("AI Research Agent started.")
print("Type 'exit' or 'quit' to stop.")


while True:

    question = input("\nYou: ").strip()

    if not question:
        continue

    # -----------------------------------------------------
    # EXIT
    # -----------------------------------------------------

    if question.lower() in ["exit", "quit"]:
        print("Agent stopped.")
        break

    lower_question = question.lower()


    # =====================================================
    # DIRECT PERSONAL MEMORY SAVE
    # =====================================================

    if should_save_personal_memory(question):

        print("TOOL: memory_save")

        save_memory(
            "user",
            question,
        )

        print("TOOL RESULT:")
        print("Memory saved successfully.")

        print("\nAI:")
        print("I'll remember that.")

        continue


    # =====================================================
    # DIRECT PERSONAL MEMORY SEARCH
    # =====================================================

    memory_query = extract_memory_query(question)

    if memory_query:

        print("TOOL: memory_search")

        memories = search_memory(memory_query)

        if not memories:

            result = (
                "I don't have that information saved yet."
            )

        else:

            # Most recent matching memory
            role, content = memories[0]
            result = content

        print("TOOL RESULT:")
        print(result)

        print("\nAI:")
        print(result)

        continue


    # =====================================================
    # DIRECT CALCULATOR
    # =====================================================

    if is_math_question(question):

        print("TOOL: calculator")

        result = calculator(question)

        print("TOOL RESULT:")
        print(result)

        print("\nAI:")
        print(f"The answer is {result}.")

        continue


    # =====================================================
    # DIRECT RAG
    # =====================================================

    if is_rag_question(question):

        answer = answer_with_rag(question)

        print("\nAI:")
        print(answer)

        continue


    # =====================================================
    # DIRECT WEB SEARCH
    # =====================================================

    # Explicit search requests are routed directly.
    # This makes the demo much more reliable with a small
    # local model such as Qwen 2.5 1.5B.

    if is_explicit_web_search(question):

        answer = answer_with_web_search(question)

        print("\nAI:")
        print(answer)

        continue


    # =====================================================
    # NORMAL AGENT
    # =====================================================

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": question,
        },
    ]


    # =====================================================
    # AGENT TOOL LOOP
    # =====================================================

    max_tool_rounds = 5

    for _ in range(max_tool_rounds):

        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
        )

        messages.append(response.message)

        tool_calls = response.message.tool_calls

        # -------------------------------------------------
        # NO TOOL CALL
        # -------------------------------------------------

        if not tool_calls:

            print("\nAI:")
            print(response.message.content)

            break


        # -------------------------------------------------
        # EXECUTE TOOL CALLS
        # -------------------------------------------------

        for tool_call in tool_calls:

            name = tool_call.function.name

            arguments = normalize_arguments(
                tool_call.function.arguments
            )

            print("TOOL:", name)
            print("ARGUMENTS:", arguments)


            # =================================================
            # CALCULATOR
            # =================================================

            if name == "calculator":

                expression = arguments.get(
                    "expression",
                    "",
                )

                result = calculator(expression)


            # =================================================
            # MEMORY SEARCH
            # =================================================

            elif name == "memory_search":

                query = arguments.get(
                    "query",
                    "",
                )

                memories = search_memory(query)

                if not memories:

                    result = (
                        "No relevant memory found."
                    )

                else:

                    result = "\n".join(
                        f"{role}: {content}"
                        for role, content in memories
                    )


            # =================================================
            # MEMORY SAVE
            # =================================================

            elif name == "memory_save":

                content = arguments.get(
                    "content",
                    "",
                )

                if content:

                    save_memory(
                        "user",
                        content,
                    )

                    result = (
                        "Memory saved successfully."
                    )

                else:

                    result = (
                        "No memory content was provided."
                    )


            # =================================================
            # RAG SEARCH
            # =================================================

            elif name == "rag_search":

                query = arguments.get(
                    "query",
                    "",
                )

                results = search_index(query)

                if not results:

                    result = (
                        "No relevant information found."
                    )

                else:

                    result = "\n\n".join(results)


            # =================================================
            # WEB SEARCH
            # =================================================

            elif name == "search_web":

                query = arguments.get(
                    "query",
                    question,
                )

                result = search_web(query)


            # =================================================
            # UNKNOWN TOOL
            # =================================================

            else:

                result = "Unknown tool."


            # =================================================
            # TOOL RESULT
            # =================================================

            print("TOOL RESULT:")
            print(result)

            messages.append(
                {
                    "role": "tool",
                    "tool_name": name,
                    "content": str(result),
                }
            )

    else:

        print("\nAI:")
        print(
            "I reached the maximum number of tool calls "
            "for this request."
        )