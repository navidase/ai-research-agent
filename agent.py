import ollama

from search import search
from memory import save_memory, search_memory
from rag import search_index


# =========================================================
# TOOLS
# =========================================================

def calculator(expression):
    return str(eval(expression))


def search_web(query):

    results = search(query)

    if not results:
        return "No search results found."

    return "\n\n".join(
        f"TITLE: {r['title']}\n"
        f"URL: {r['url']}\n"
        f"CONTENT: {r['content']}"
        for r in results
    )


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
        "according to",
        "according to the knowledge",
        "what is navid learning",
        "what does navid learn",
        "what is navid learning",
    ]

    return any(
        keyword in q
        for keyword in keywords
    )


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
                "Use this tool whenever the question asks about "
                "information contained in the local knowledge base, "
                "knowledge documents, company information, or stored "
                "knowledge."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The information to search for "
                            "in the local knowledge base."
                        )
                    }
                },
                "required": ["query"]
            }
        }
    },


    # -----------------------------------------------------
    # MEMORY SEARCH
    # -----------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "memory_search",
            "description": (
                "Use this tool whenever the user asks about "
                "personal information that may have been saved "
                "from previous conversations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "What personal information to search "
                            "for in memory."
                        )
                    }
                },
                "required": ["query"]
            }
        }
    },


    # -----------------------------------------------------
    # MEMORY SAVE
    # -----------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "memory_save",
            "description": (
                "Use this tool whenever the user tells you "
                "important personal information that should be "
                "remembered for future conversations, such as "
                "their name, location, job, preferences, goals, "
                "or other stable personal facts."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": (
                            "The personal information that should "
                            "be saved."
                        )
                    }
                },
                "required": ["content"]
            }
        }
    },


    # -----------------------------------------------------
    # CALCULATOR
    # -----------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": (
                "ONLY use this tool for mathematical calculations "
                "and arithmetic expressions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "A mathematical expression such as "
                            "25 * 99."
                        )
                    }
                },
                "required": ["expression"]
            }
        }
    },


    # -----------------------------------------------------
    # WEB SEARCH
    # -----------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": (
                "Use this tool for current, latest, recent, "
                "news, research, or web information."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The query to search on the web."
                        )
                    }
                },
                "required": ["query"]
            }
        }
    }

]


# =========================================================
# MAIN AGENT LOOP
# =========================================================

while True:

    question = input("\nYou: ")

    # -----------------------------------------------------
    # EXIT
    # -----------------------------------------------------

    if question.lower().strip() in ["exit", "quit"]:

        print("Agent stopped.")

        break


    lower_question = question.lower().strip()


    # =====================================================
    # DIRECT MEMORY SAVE
    # =====================================================

    if lower_question.startswith("my name is "):

        name = question[11:].strip()

        print("TOOL: memory_save")

        save_memory(
            "user",
            f"My name is {name}"
        )

        print("TOOL RESULT:")
        print("Memory saved successfully.")

        print("\nAI:")
        print(f"Nice to meet you, {name}.")

        continue


    if lower_question.startswith("i live in "):

        location = question[10:].strip()

        print("TOOL: memory_save")

        save_memory(
            "user",
            f"I live in {location}"
        )

        print("TOOL RESULT:")
        print("Memory saved successfully.")

        print("\nAI:")
        print(
            f"I'll remember that you live in {location}."
        )

        continue


    if lower_question.startswith("i work "):

        print("TOOL: memory_save")

        save_memory(
            "user",
            question
        )

        print("TOOL RESULT:")
        print("Memory saved successfully.")

        print("\nAI:")
        print("I'll remember that.")

        continue


    # =====================================================
    # DIRECT MEMORY SEARCH
    # =====================================================

    if (
        "what is my name" in lower_question
        or "what's my name" in lower_question
    ):

        print("TOOL: memory_search")

        memories = search_memory("My name is")

        if not memories:

            result = "I don't know your name yet."

        else:

            result = memories[0][1]

        print("TOOL RESULT:")
        print(result)

        print("\nAI:")
        print(result)

        continue


    # =====================================================
    # DIRECT CALCULATOR ROUTING
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
    # DIRECT RAG ROUTING
    # =====================================================

    if is_rag_question(question):

        print("TOOL: rag_search")

        results = search_index(question)

        if not results:

            result = "No relevant information found."

        else:

            result = "\n\n".join(results)

        print("TOOL RESULT:")
        print(result)


        # Send retrieved information to Qwen

        response = ollama.chat(

            model="qwen2.5:1.5b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "Answer the user's question using ONLY "
                        "the provided knowledge base. "
                        "Do not invent information."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Question:\n{question}\n\n"
                        f"Knowledge base:\n{result}"
                    )
                }
            ]
        )

        print("\nAI:")
        print(response.message.content)

        continue


    # =====================================================
    # NORMAL AGENT
    # =====================================================

    messages = [
        {
            "role": "user",
            "content": question
        }
    ]


    # =====================================================
    # AGENT TOOL LOOP
    # =====================================================

    while True:

        response = ollama.chat(

            model="qwen2.5:1.5b",

            messages=messages,

            tools=tools
        )


        messages.append(response.message)


        # -------------------------------------------------
        # NO TOOL
        # -------------------------------------------------

        if not response.message.tool_calls:

            print("\nAI:")
            print(response.message.content)

            break


        # -------------------------------------------------
        # TOOL CALLS
        # -------------------------------------------------

        for tool_call in response.message.tool_calls:

            name = tool_call.function.name

            arguments = tool_call.function.arguments


            print("TOOL:", name)

            print(
                "ARGUMENTS:",
                arguments
            )


            # =================================================
            # CALCULATOR
            # =================================================

            if name == "calculator":

                result = calculator(
                    arguments["expression"]
                )


            # =================================================
            # MEMORY SEARCH
            # =================================================

            elif name == "memory_search":

                memories = search_memory(
                    arguments["query"]
                )

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

                content = arguments["content"]

                save_memory(
                    "user",
                    content
                )

                result = (
                    "Memory saved successfully."
                )


            # =================================================
            # RAG SEARCH
            # =================================================

            elif name == "rag_search":

                results = search_index(
                    arguments["query"]
                )

                if not results:

                    result = (
                        "No relevant information found."
                    )

                else:

                    result = "\n\n".join(
                        results
                    )


            # =================================================
            # WEB SEARCH
            # =================================================

            elif name == "search_web":

                result = search_web(
                    arguments["query"]
                )


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


            messages.append({

                "role": "tool",

                "tool_name": name,

                "content": str(result)

            })