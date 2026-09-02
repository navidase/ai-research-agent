# AI Research Agent

A practical AI research assistant built with Python, local LLMs, web search, persistent memory, RAG, and tool calling.

The agent can research current information from the web, retrieve information from a local knowledge base, remember user preferences, perform safe calculations, and combine these capabilities inside a conversational interface.

## What It Can Do

* 🔎 Search the web for current information
* 📚 Retrieve information from a local knowledge base using RAG
* 🧠 Store and retrieve persistent user memory
* 🧮 Perform safe mathematical calculations
* 🤖 Run locally using Ollama and Qwen
* 🛠 Route requests to specialized tools
* 💬 Provide both CLI and Streamlit chat interfaces
* 🔐 Load API credentials securely from environment variables

## Example Use Cases

This architecture can be adapted for:

* AI research assistants
* Internal company knowledge assistants
* Document and knowledge-base chatbots
* Business research automation
* Customer support assistants
* AI workflow automation
* Custom RAG applications

## Architecture

```text
User
  │
  ▼
AI Research Agent
  │
  ├── Web Search ─────── Tavily
  │
  ├── Memory ─────────── SQLite
  │
  ├── RAG ────────────── Ollama Embeddings
  │
  └── Calculator ─────── Safe AST Evaluation
  │
  ▼
Qwen 2.5 via Ollama
  │
  ▼
Final Response
```

## Tech Stack

* Python
* Streamlit
* Ollama
* Qwen 2.5
* Nomic Embed Text
* Tavily Search API
* SQLite
* Custom RAG pipeline
* Vector embeddings
* Cosine similarity
* Tool calling
* python-dotenv

## Project Structure

```text
ai-research-agent/
│
├── agent.py          # Main CLI agent
├── app.py            # Streamlit web interface
├── tools.py          # Agent tools
├── search.py         # Tavily web search
├── memory.py         # Persistent SQLite memory
├── rag.py            # RAG and vector retrieval
├── build_index.py    # Knowledge-base indexing
├── knowledge.txt     # Example local knowledge
├── requirements.txt
└── .gitignore
```

## Installation

Clone the repository:

```bash
git clone https://github.com/navidase/ai-research-agent.git
cd ai-research-agent
```

Create a virtual environment:

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

## Ollama Models

Install Ollama and download the required models:

```bash
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
```

## Tavily API Configuration

Create a `.env` file:

```env
TAVILY_API_KEY=your_tavily_api_key
```

API credentials are not stored in the source code.

## Build the RAG Index

```bash
python build_index.py
```

## Run the Web App

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Run the CLI Agent

```bash
python agent.py
```

## Example

```text
You:
My favorite programming language is Python.

AI:
I'll remember that.

You:
What is my favorite programming language?

AI:
My favorite programming language is Python.
```

The agent can also perform web research:

```text
You:
Search the web for the latest AI news.

Agent:
→ Calls Web Search
→ Retrieves current sources
→ Sends retrieved context to the local LLM
→ Generates a summarized answer
```

## Security

The project includes several security-oriented implementation choices:

* API keys are stored in environment variables
* `.env` is excluded from Git
* The calculator does not use unrestricted Python `eval()`
* User memory is stored locally
* The LLM can run completely locally through Ollama

## Portfolio Purpose

This project demonstrates practical AI engineering skills including:

* LLM integration
* AI agents
* RAG
* embeddings
* persistent memory
* external API integration
* tool routing
* local AI inference
* Streamlit application development

The architecture can be extended into production-oriented AI assistants and custom business automation systems.
