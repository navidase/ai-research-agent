# AI Research Agent

A portfolio prototype for exploring practical AI applications with Python, Ollama, web search, local document retrieval, and persistent memory.

The project includes a Streamlit chat interface and a separate command-line agent. It is under active development and is not presented as a production-ready system.

## Features

- Display retrieved source filenames, chunk numbers, and excerpts beneath knowledge-base answers
- Search the web through Tavily
- Retrieve text from a local knowledge base using RAG
- Store and retrieve user memory
- Perform mathematical calculations
- Run language models locally through Ollama
- Interact through Streamlit or the command line

## How It Works

The two interfaces use different routing approaches:

| Interface | Entry point | Routing approach |
|---|---|---|
| Streamlit web app | `app.py` | Rule-based routing to supported capabilities |
| Command-line agent | `agent.py` | Explores LLM tool calling alongside explicit routing rules |

The web interface does not currently use the same LLM tool-calling loop as the CLI agent.

For local knowledge questions, the application retrieves relevant text from an index and passes it to the language model as context.

## Tech Stack

| Component | Technology |
|---|---|
| Application language | Python |
| Web interface | Streamlit |
| Local model runtime | Ollama |
| Language model | Qwen 2.5 |
| Embedding model | Nomic Embed Text |
| Web search | Tavily |
| Persistent memory | SQLite |
| Retrieval | Custom embedding index and cosine similarity |
| Configuration | Environment variables and python-dotenv |

## Project Structure

```text
ai-research-agent/
├── agent.py          # Command-line agent
├── app.py            # Streamlit web interface
├── tools.py          # Tool implementations
├── search.py         # Tavily integration
├── memory.py         # Persistent memory
├── rag.py            # Indexing and retrieval
├── build_index.py    # Build the local knowledge index
├── knowledge.txt     # Sample knowledge base
├── requirements.txt  # Python dependencies
└── .gitignore
```

## Prerequisites

- Python with pip and virtual environment support
- Git
- Ollama installed and running
- Sufficient memory and storage for the selected models
- A Tavily API key for web search

Initial dependency installation and model downloads require internet access. Web search sends queries to an external service; the complete application is not fully offline.

## Installation — Windows CMD

These commands use the virtual environment's Python executable directly. Activation is not required.

### 1. Clone the repository

```bat
git clone https://github.com/navidase/ai-research-agent.git
cd ai-research-agent
```

### 2. Create a virtual environment

```bat
python -m venv .venv
```

### 3. Install dependencies

```bat
.venv\Scripts\python -m pip install -r requirements.txt
```

### 4. Download the Ollama models

Make sure Ollama is installed and running, then run:

```bat
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
```

The model names must match those configured in the source code.

### 5. Configure Tavily

Create a file named `.env` in the project root:

```env
TAVILY_API_KEY=your_tavily_api_key
```

Replace the placeholder with your own key. Do not commit this file.

Web search requires valid credentials and access to the Tavily service.

### 6. Build the knowledge index

Review or edit `knowledge.txt`, then run:

```bat
.venv\Scripts\python build_index.py
```

Rebuild the index whenever you change the knowledge file or embedding model.

### 7. Start the web app

```bat
.venv\Scripts\python -m streamlit run app.py
```

Open the Local URL printed in the terminal, usually:

```text
http://localhost:8501
```

Keep the terminal open while using the application. Enter questions in the browser.

To stop the server, press `Ctrl+C` in the terminal.

## Alternative Local Port

If the default port is occupied or an older session is still running:

```bat
.venv\Scripts\python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502
```

Then open:

```text
http://127.0.0.1:8502
```

This address is accessible on your own computer; it is not a public deployment.

## Run the CLI Agent

For the command-line interface:

```bat
.venv\Scripts\python agent.py
```

Enter questions in the terminal.

Use `app.py` when launching Streamlit. Do not launch the command-line files with `streamlit run`.

## Example Prompts

### Local knowledge retrieval

```text
According to the knowledge base, which services does the company offer?
Answer in three short bullet points.
```

For the included sample knowledge, the expected services are:

- Customer support agents
- Research agents
- Workflow automation

### Missing information

```text
According to the knowledge base, what is the company's monthly service price?
```

The sample knowledge does not specify a price. The desired behavior is to acknowledge that information is missing rather than invent an amount.

### Memory

```text
My favorite programming language is Python.
```

Then ask:

```text
What is my favorite programming language?
```

Remembering a fact within one session does not by itself verify persistence across application restarts.

### Calculator

```text
25 * 99
```

Expected result: `2475`.

### Web search

```text
Search the web for the latest AI news.
```

This requires a working Tavily connection.

## Current Limitations

- The included knowledge base is small and does not demonstrate large-scale or multi-document retrieval.
- The web app uses rule-based routing, which can misclassify requests.
- Generated answers may contain errors or unsupported claims.
- Local inference speed depends on hardware and model size.
- Web search depends on external service availability and credentials.
- Authentication, user isolation, and production deployment are outside the current demo scope.

## Troubleshooting

| Problem | What to check |
|---|---|
| A terminal `You:` prompt appears instead of a web chat | Launch `app.py` with Streamlit. |
| The browser opens an old session | Check the terminal's Local URL and port. |
| The model cannot be found | Download the model and confirm its name matches the code. |
| Knowledge retrieval fails or uses old content | Rebuild the index after changing `knowledge.txt`. |
| Tavily returns an access error | Check API configuration and the service's error details. |
| A network request fails | Check connectivity and service availability. |
| Responses are slow | Check local hardware capacity and model execution. |

## Privacy and Security Considerations

- Keep API keys outside source files.
- Ensure `.env` is ignored by Git before committing.
- Review staged files for credentials, private documents, memory databases, and generated indexes.
- Local storage does not automatically provide encryption or access control.
- Web search queries leave the local machine.
- Review tool implementations before using the application with sensitive data or exposing it publicly.

These are development precautions, not a security certification.

## Planned Improvements

- Evaluate retrieval using a larger set of documents
- Test answerable and unanswerable questions
- Improve routing and external-service error handling

## Portfolio Purpose

This project documents hands-on work with local language models, retrieval, memory, tool integration, and conversational interfaces.

Possible future adaptations include internal knowledge assistants, customer support prototypes, and business research tools. Each would require additional evaluation and engineering for its intended use.
