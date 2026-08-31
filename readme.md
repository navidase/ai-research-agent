# AI Research Agent

An AI-powered research assistant built with Python and Ollama.

## Features

* 🤖 Local LLM powered by Ollama
* 🔎 Web search
* 🧠 Persistent user memory
* 📚 RAG over local knowledge
* 🧮 Calculator tool
* 🛠️ Tool calling
* 🔗 Multiple tools working together

## Architecture

The agent uses a tool-calling architecture where the LLM decides which tool should handle each request.

### Available Tools

| Tool          | Purpose                          |
| ------------- | -------------------------------- |
| Calculator    | Mathematical calculations        |
| Web Search    | Current web information          |
| Memory Search | Retrieve saved user information  |
| Memory Save   | Store important user information |
| RAG Search    | Search the local knowledge base  |

## Tech Stack

* Python
* Ollama
* Qwen 2.5
* Nomic Embed Text
* ChromaDB
* Sentence Transformers
* RAG
* Tool Calling

## Example

```text
You: what is my name?

TOOL: memory_search
TOOL RESULT:
My name is Navid

AI:
My name is Navid
```

## Project Structure

```text
ai-research-agent/
│
├── agent.py
├── rag.py
├── memory.py
├── search.py
├── knowledge.txt
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install the required Ollama models:

```bash
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
```

Run the agent:

```bash
python agent.py
```

## Goal

This project is part of my AI engineering learning journey, focused on building practical AI agents with Python, RAG, memory, tool calling, and LLM engineering.
