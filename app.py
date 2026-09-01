import streamlit as st
import ollama

from search import search
from memory import save_memory, search_memory
from rag import search_index
from tools import calculator


MODEL_NAME = "qwen2.5:1.5b"


st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔎",
    layout="centered",
)


st.title("🔎 AI Research Agent")

st.caption(
    "AI agent with Web Search, RAG, Memory and Calculator"
)


# =========================================================
# SESSION CHAT MEMORY
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# =========================================================
# HELPERS
# =========================================================

def web_search(query):

    results = search(query)

    if not results:
        return "No web results found."

    formatted = []

    for item in results[:5]:

        title = item.get("title", "No title")
        url = item.get("url", "")
        content = item.get("content", "")[:1000]

        formatted.append(
            f"""
TITLE: {title}

URL: {url}

CONTENT:
{content}
"""
        )

    return "\n\n".join(formatted)


def should_use_web(question):

    q = question.lower()

    keywords = [
        "latest",
        "current",
        "today",
        "news",
        "search web",
        "search the web",
        "look up",
        "recent",
    ]

    return any(word in q for word in keywords)


def should_use_rag(question):

    q = question.lower()

    keywords = [
        "knowledge base",
        "document",
        "local knowledge",
        "according to the knowledge",
    ]

    return any(word in q for word in keywords)


def should_save_memory(question):

    q = question.lower().strip()

    if q.startswith("my ") and " is " in q:
        return True

    prefixes = [
        "i like ",
        "i love ",
        "i prefer ",
        "i live in ",
        "i work ",
        "my name is ",
    ]

    return any(q.startswith(x) for x in prefixes)


def memory_query(question):

    q = question.lower().strip()

    prefixes = [
        "what is my ",
        "what's my ",
        "do you remember my ",
    ]

    for prefix in prefixes:

        if q.startswith(prefix):

            return q[len(prefix):].rstrip(" ?.")

    return None


def is_math(question):

    cleaned = question.replace(" ", "")

    if not cleaned:
        return False

    allowed = "0123456789+-*/().%"

    return (
        any(x.isdigit() for x in cleaned)
        and all(x in allowed for x in cleaned)
    )


# =========================================================
# AGENT
# =========================================================

def run_agent(question):

    # -----------------------------------------------------
    # SAVE MEMORY
    # -----------------------------------------------------

    if should_save_memory(question):

        save_memory(
            "user",
            question
        )

        return "I'll remember that."


    # -----------------------------------------------------
    # SEARCH MEMORY
    # -----------------------------------------------------

    query = memory_query(question)

    if query:

        memories = search_memory(query)

        if memories:

            return memories[0][1]

        return "I don't have that information saved yet."


    # -----------------------------------------------------
    # CALCULATOR
    # -----------------------------------------------------

    if is_math(question):

        result = calculator(question)

        return f"The answer is **{result}**."


    # -----------------------------------------------------
    # WEB SEARCH
    # -----------------------------------------------------

    if should_use_web(question):

        results = web_search(question)

        if results == "No web results found.":
            return results

        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": """
You are an AI research assistant.

Answer using ONLY the supplied web search results.

Summarize the most relevant information.

Include useful source URLs.

Never say you cannot access the internet because
web results have already been supplied.

Do not invent facts.
""",
                },
                {
                    "role": "user",
                    "content": f"""
QUESTION:

{question}


WEB SEARCH RESULTS:

{results}
""",
                },
            ],
        )

        return response.message.content


    # -----------------------------------------------------
    # RAG
    # -----------------------------------------------------

    if should_use_rag(question):

        results = search_index(question)

        if not results:
            return "No relevant information found in the knowledge base."

        context = "\n\n".join(results)

        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": """
Answer the user's question using the provided
knowledge-base context.

Do not invent information that is not present
in the context.
""",
                },
                {
                    "role": "user",
                    "content": f"""
QUESTION:

{question}


KNOWLEDGE BASE:

{context}
""",
                },
            ],
        )

        return response.message.content


    # -----------------------------------------------------
    # NORMAL CHAT
    # -----------------------------------------------------

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": """
You are a useful AI Research Agent.

You can assist with research, programming,
AI, machine learning and general questions.

Be accurate and concise.
""",
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    return response.message.content


# =========================================================
# CHAT INPUT
# =========================================================

question = st.chat_input(
    "Ask the AI Research Agent..."
)


if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)


    with st.chat_message("assistant"):

        with st.spinner("Researching..."):

            try:

                answer = run_agent(question)

            except Exception as e:

                answer = f"Error: {e}"

        st.markdown(answer)


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )