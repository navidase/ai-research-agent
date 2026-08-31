import ollama
import json

conversation = [] 

from search import search
from tools import get_time, calculator
from memory import save_memory, get_memories, search_memory

ROUTER_PROMPT = """
You are ONLY a JSON tool router.

You MUST NOT answer the user's question.
You MUST NOT explain anything.
You MUST NOT apologize.
You MUST NOT say you cannot browse.
You MUST NOT mention your capabilities.

Your ONLY job is to select a tool.

Available tools:

CALCULATOR
TIME
DONE
SEARCH
LLM

Use CALCULATOR for math.
Use TIME for current time.
Use SEARCH for latest, current, recent, news, web, or research information.
Use LLM for normal questions.
Use DONE when enough information is already available
and no tool is needed.

If the user asks for CURRENT or LATEST information, ALWAYS choose SEARCH.

IMPORTANT FOR MEMORY QUESTIONS:

Questions about the user's name, preferences, previous messages,
or remembered information MUST use LLM.

Examples:

User: what is my name?
Output:
{"tool":"LLM"}

User: what did I tell you earlier?
Output:
{"tool":"LLM"}

User: what do you remember about me?
Output:
{"tool":"LLM"}


Return ONLY valid JSON.

Examples:

{"tool":"CALCULATOR","expression":"25 * 99"}

{"tool":"TIME"}

{"tool":"SEARCH"}

{"tool":"LLM"}

{"tool":"DONE"}
"""

def route(question):
    response = ollama.chat(
        model="qwen2.5:1.5b",
        messages=[
            {
                "role": "system",
                "content": ROUTER_PROMPT
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    content = response["message"]["content"].strip()

    print("RAW ROUTER:", content)

    try:
        decision = json.loads(content)

        if not isinstance(decision, dict):
            return {"tool": "LLM"}

        if "tool" not in decision:
            return {"tool": "LLM"}

        return decision

    except json.JSONDecodeError:
        return {"tool": "LLM"}



def run_tool(decision, question):
    tool_name = decision["tool"]

    print("TOOL:", tool_name)

    if tool_name == "CALCULATOR":
        expression = decision.get("expression")

        if not expression:
            return "Calculator expression missing."

        return str(calculator(expression))

    elif tool_name == "TIME":
        return get_time()

    elif tool_name == "SEARCH":
        results = search(question)

        if not results:
            return "No search results found."

        context = "\n\n".join(
            f"TITLE: {result['title']}\n"
            f"URL: {result['url']}\n"
            f"CONTENT: {result['content']}"
            for result in results
        )

        return context

    elif tool_name == "LLM":

        memories = search_memory(question)

        print("MEMORIES:", memories)

        memory_text = "\n".join(
            f"{role}: {content}"
            for role, content in memories
        )

        print("MEMORY TEXT:", memory_text)

        messages = [
            {
                "role": "system",
                "content": f"""
You are an AI assistant.

Use the relevant memory below when answering.

MEMORY:
{memory_text}

If the memory contains the answer, use it.
Do not invent personal information.
"""
            }
        ]

        messages.extend(conversation)

        response = ollama.chat(
            model="qwen2.5:1.5b",
            messages=messages
        )

        assistant_answer = response["message"]["content"]

        conversation.append({
            "role": "assistant",
            "content": assistant_answer
        })

        save_memory("assistant", assistant_answer)

        return assistant_answer

    return "Unknown tool."


def final_answer(question, tool_name, tool_result):
    response = ollama.chat(
        model="qwen2.5:1.5b",
        messages=[
            {
                "role": "system",
                "content": """
You are the final answer generator.

Answer the user's question using the tool result.

If the tool was SEARCH:
- Summarize the search results.
- Use only information from the results.
- Do not invent facts.
- Mention important sources when useful.

If the tool was CALCULATOR:
- Give the calculation result directly.

If the tool was LLM:
- Answer using the provided memory and conversation.

Be concise and clear.
"""
            },
            {
                "role": "user",
                "content": f"""
USER QUESTION:
{question}

TOOL USED:
{tool_name}

TOOL RESULT:
{tool_result}
"""
            }
        ]
    )

    return response["message"]["content"]


def run_agent(question):
    conversation.append({
        "role": "user",
        "content": question
    })

    save_memory("user", question)

    decision = route(question)

    print("DECISION:", decision)

    tool_name = decision["tool"]

    if tool_name == "DONE":
        print("\nAI:")
        print("I already have enough information.")
        return

    tool_result = run_tool(decision, question)

    print("\nTOOL RESULT:")
    print(tool_result)

    answer = final_answer(question, tool_name, tool_result)

    print("\nAI:")
    print(answer)

    return answer


while True:
    question = input("\nYou: ")

    if question.lower() in ["exit", "quit"]:
        print("Agent stopped.")
        break

    run_agent(question)