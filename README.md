# Saudi Tender AI Agent

An AI-powered Tender Management and Analysis System for processing, searching, analyzing, and comparing Saudi tender documents.

The system combines **FastAPI, PostgreSQL, Redis, Qdrant, LangGraph, RAG, LLMs, and Streamlit** into a multi-agent architecture.

---

## 🚀 Features

* 🔐 User authentication and authorization
* 📂 Project management
* 📄 Tender PDF upload and processing
* 🔎 Semantic search over tender documents
* 🧠 Retrieval-Augmented Generation (RAG)
* 🔀 Multi-agent routing using LangGraph
* 🗄️ SQL agent for database-related questions
* ⚠️ Risk analysis
* 📊 Tender report generation
* ⚖️ Tender comparison
* 💬 Conversational question answering
* 📚 Source/page references for RAG answers
* 🐳 Docker Compose deployment
* 📈 LangSmith tracing and monitoring

---

# 🏗️ System Architecture

```text
                         ┌──────────────────┐
                         │     Streamlit    │
                         │     Frontend     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │      Backend     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   ChatService    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    LangGraph     │
                         │    Supervisor    │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
        ┌──────────┐        ┌──────────┐       ┌──────────┐
        │ SQLAgent │        │ RAGAgent  │       │ Report   │
        │          │        │           │       │ Agent    │
        └────┬─────┘        └─────┬─────┘       └──────────┘
             │                    │
             ▼                    ▼
        PostgreSQL             Qdrant
                                  │
                                  ▼
                            Embeddings
                                  │
                                  ▼
                             Reranker
                                  │
                                  ▼
                                LLM
```

Additional agents:

```text
RiskAgent
CompareAgent
```

---

# 🧠 Multi-Agent Architecture

The system uses a Supervisor Agent to determine which agent should handle the user's question.

## Available Agents

### 1. Supervisor Agent

The Supervisor classifies the user's question into one of:

```text
sql
rag
report
risk
compare
```

Example:

```text
how many tenders
```

→ `sql`

```text
what is the tender number?
```

→ `rag`

```text
generate a report
```

→ `report`

```text
what are the risks?
```

→ `risk`

```text
compare these two tenders
```

→ `compare`

---

## 2. SQL Agent

The SQL Agent handles questions about information stored in the application database.

Examples:

```text
how many tenders?
```

```text
how many projects?
```

```text
list all tenders
```

```text
what are the tender statuses?
```

The SQL Agent queries PostgreSQL instead of searching the tender PDF.

Example flow:

```text
User
 ↓
Supervisor
 ↓
SQLAgent
 ↓
PostgreSQL
 ↓
Answer
```

---

## 3. RAG Agent

The RAG Agent handles questions about the content of tender documents.

Examples:

```text
What is the tender number?
```

```text
What are the technical requirements?
```

```text
What is the deadline?
```

```text
What are the penalties?
```

The RAG pipeline is:

```text
Question
   ↓
Embedding
   ↓
Vector Search
   ↓
BM25 Search
   ↓
RRF Fusion
   ↓
Cross-Encoder Reranking
   ↓
Top Context
   ↓
LLM
   ↓
Answer + Sources
```

---

# 🔎 RAG Pipeline

## 1. Document Processing

Uploaded tender documents are processed and divided into chunks.

Each chunk contains information such as:

```text
page_content
metadata
page
source
```

---

## 2. Embeddings

The system uses a Sentence Transformer embedding model to convert text into vectors.

Current configuration can use:

```text
BAAI/bge-m3
```

These vectors are stored in Qdrant.

---

## 3. Vector Search

The user's question is converted into an embedding and compared against stored document vectors.

This retrieves semantically similar chunks.

---

## 4. BM25 Search

The system also performs lexical keyword-based retrieval using BM25.

This is useful when the exact terminology in the question appears inside the tender.

---

# 🔀 RRF — Reciprocal Rank Fusion

The system combines results from different retrieval methods using **Reciprocal Rank Fusion (RRF)**.

Conceptually:

```text
Vector Search
      +
    BM25
      ↓
     RRF
      ↓
Combined Ranking
```

RRF gives higher importance to documents that appear near the top of multiple result lists.

This improves retrieval robustness compared with relying on only one search method.

---

# 🎯 Cross-Encoder Reranking

After retrieving candidate chunks, the system uses a Cross-Encoder reranker to score the relevance between:

```text
Question
+
Retrieved Chunk
```

The highest scoring chunks are passed to the LLM.

Example:

```text
Question
   ↓
Retrieve 20 chunks
   ↓
Cross-Encoder
   ↓
Top 10 chunks
   ↓
LLM
```

---

# 🗄️ Database Architecture

The project uses PostgreSQL for persistent application data.

Main entities include:

```text
User
Project
Tender
```

Relationship:

```text
User
 │
 └── Projects
       │
       └── Tenders
```

A user can own multiple projects.

A project can contain multiple tenders.

---

# 🧠 Vector Database

Qdrant is used as the vector database.

Each tender can have its own collection.

Example:

```text
tender_8b106cbce9f64d10ad413f93d194b84b
```

This isolates tender documents and allows retrieval for a specific tender.

---

# ⚡ Redis

Redis is used for temporary application data and conversational memory.

Typical architecture:

```text
Session
   ↓
Redis List
   ↓
Conversation Messages
```

The system can retain recent conversation history while avoiding unnecessary database queries.

---

# 🌐 Backend

The backend is implemented using FastAPI.

Example endpoints:

```text
POST /auth/register
POST /auth/login

GET  /projects
POST /projects

GET  /tenders/project/{project_id}
POST /tenders/upload/{project_id}

POST /chat

POST /reports/{tender_id}

POST /compare

POST /export/
```

---

# 💬 Chat Flow

A chat request follows this architecture:

```text
POST /chat
      ↓
ChatService
      ↓
LangGraph
      ↓
SupervisorAgent
      ↓
Intent Classification
      ↓
┌────────┬────────┬────────┬────────┬────────┐
│  SQL   │  RAG   │ Report │  Risk  │Compare │
└────────┴────────┴────────┴────────┴────────┘
```

The important design decision is that `ChatService` invokes the LangGraph instead of calling the RAG service directly.

Example:

```python
result = graph.invoke(state)
```

This allows the Supervisor to decide which agent should process the question.

---

# 🖥️ Streamlit Frontend

The frontend is implemented using Streamlit.

Main pages:

```text
Login
Register
Dashboard
Upload
Chat
Report
Compare
```

Typical workflow:

```text
Register
   ↓
Login
   ↓
Create Project
   ↓
Upload Tender
   ↓
Select Tender
   ↓
Chat / Report / Compare
```

---

# 📤 Tender Upload Flow

```text
User uploads PDF
       ↓
FastAPI
       ↓
Document Processing
       ↓
Text Extraction
       ↓
Chunking
       ↓
Embeddings
       ↓
Qdrant
       ↓
Tender ready for RAG
```

---

# 📊 Reports

The system can generate tender reports such as:

```text
Executive Summary
Risk Report
```

The report service retrieves relevant tender information and sends the context to the LLM to generate the final report.

---

# ⚖️ Tender Comparison

The Compare Agent can compare two tenders based on available document information.

Example:

```text
Tender A
   +
Tender B
   ↓
Compare Agent
   ↓
LLM
   ↓
Comparison
```

---

# ⚠️ Risk Analysis

The Risk Agent retrieves relevant tender information related to:

```text
Risks
Penalties
Obligations
Requirements
Deadlines
```

and generates a structured risk analysis.

---

# 🔐 Authentication

The system uses token-based authentication.

Typical flow:

```text
Register
   ↓
Login
   ↓
Access Token
   ↓
Authorization Header
```

Example:

```http
Authorization: Bearer <token>
```

---

# 🐳 Docker

The project uses Docker Compose.

Main services:

```text
fastapi
postgres
redis
qdrant
streamlit
```

Architecture:

```text
Docker Compose
│
├── FastAPI
├── PostgreSQL
├── Redis
├── Qdrant
└── Streamlit
```

---

# ⚙️ Environment Variables

Create a `.env` file.

Example:

```env
DATABASE_URL=postgresql://postgres:password@postgres:5432/tender_db

REDIS_URL=redis://redis:6379

QDRANT_URL=http://qdrant:6333

GOOGLE_API_KEY=your_google_api_key

GEMINI_API_KEY=your_gemini_api_key

OPENROUTER_API_KEY=your_openrouter_api_key

LANGSMITH_TRACING=true

LANGSMITH_API_KEY=your_langsmith_api_key

LANGSMITH_PROJECT=Saudi Tender Agent
```

Do not commit `.env` to Git.

---

# 🚀 Running the Project

## 1. Clone the repository

```bash
git clone <repository-url>
cd Saudi-Tender-ai-project
```

## 2. Configure environment variables

Create:

```text
.env
```

and add the required API keys.

## 3. Build and start containers

```bash
docker compose up -d --build
```

## 4. Check containers

```bash
docker compose ps
```

Expected services:

```text
ai_fastapi
ai_streamlit
ai_postgres
ai_redis
ai_qdrant
```

---

# 🔍 View Logs

FastAPI:

```bash
docker logs -f ai_fastapi
```

Streamlit:

```bash
docker logs -f ai_streamlit
```

---

# 🛑 Stop Services

```bash
docker compose down
```

---

# 🔄 Restart Services

```bash
docker compose restart
```

---

# 🧪 Testing

Run the application:

```bash
docker compose up -d
```

Then test:

```text
Register
Login
Create Project
Upload Tender
Ask Questions
Generate Report
Compare Tenders
```

---

# 🧠 Example Questions

## Database Questions

```text
how many tenders?
```

Expected route:

```text
Supervisor → SQLAgent → PostgreSQL
```

---

## Tender Questions

```text
what is the tender number?
```

Expected route:

```text
Supervisor → RAGAgent → Qdrant → Reranker → LLM
```

---

## Risk Questions

```text
what are the risks in this tender?
```

Expected route:

```text
Supervisor → RiskAgent
```

---

## Report Questions

```text
generate an executive summary
```

Expected route:

```text
Supervisor → ReportAgent
```

---

## Comparison Questions

```text
compare these two tenders
```

Expected route:

```text
Supervisor → CompareAgent
```

---

# 📈 LangSmith

LangSmith is used for tracing and monitoring LLM and agent execution.

The project can be configured with:

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=Saudi Tender Agent
```

Tracing helps identify:

* Slow LLM calls
* RAG latency
* Agent routing
* Retrieval performance
* Prompt execution
* Errors

Example trace:

```text
Chat
 ↓
Supervisor
 ↓
RAGAgent
 ↓
Embedding
 ↓
Vector Search
 ↓
BM25
 ↓
RRF
 ↓
Reranker
 ↓
LLM
```

---

# 📁 Project Structure

```text
Saudi-Tender-ai-project/
│
├── app/
│   │
│   ├── agents/
│   │   ├── supervisor_agent.py
│   │   ├── rag_agent.py
│   │   ├── sql_agent.py
│   │   ├── report_agent.py
│   │   ├── risk_agent.py
│   │   └── compare_agent.py
│   │
│   ├── graph/
│   │   ├── graph.py
│   │   └── state.py
│   │
│   ├── services/
│   │   ├── rag_service.py
│   │   ├── embedding_service.py
│   │   ├── reranker_service.py
│   │   ├── vector_service.py
│   │   ├── llm_service.py
│   │   └── ...
│   │
│   ├── database/
│   │   ├── models/
│   │   └── ...
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── projects.py
│   │   ├── tenders.py
│   │   ├── chat.py
│   │   └── ...
│   │
│   ├── schemas/
│   │
│   ├── evaluation/
│   │
│   └── main.py
│
├── streamlit_app/
│   ├── pages/
│   │   ├── Login.py
│   │   ├── Register.py
│   │   ├── Dashboard.py
│   │   ├── Upload.py
│   │   ├── Chat.py
│   │   ├── Report.py
│   │   └── Compare.py
│   │
│   ├── api.py
│   └── auth.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
├── .env
├── .gitignore
├── .dockerignore
└── README.md
```

---

# 🔒 Git & Docker Ignore

Sensitive and generated files should not be committed.

Examples:

```text
.env
.venv
__pycache__
*.pyc
*.log
datasets
models
checkpoints
qdrant_storage
postgres_data
redis_data
```

---

# 🛠️ Technologies

| Technology            | Purpose                   |
| --------------------- | ------------------------- |
| Python                | Main programming language |
| FastAPI               | Backend API               |
| Streamlit             | Frontend                  |
| PostgreSQL            | Relational database       |
| SQLAlchemy            | ORM                       |
| Redis                 | Cache / memory            |
| Qdrant                | Vector database           |
| LangGraph             | Agent orchestration       |
| LangChain             | LLM/RAG ecosystem         |
| Sentence Transformers | Embeddings                |
| Cross-Encoder         | Reranking                 |
| BM25                  | Keyword retrieval         |
| RRF                   | Retrieval fusion          |
| Gemini                | LLM                       |
| OpenRouter            | LLM gateway               |
| LangSmith             | Observability             |
| Docker                | Containerization          |
| Alembic               | Database migrations       |

---

# 🎯 Project Goal

The goal of the Saudi Tender AI Agent is to provide an intelligent assistant capable of helping users analyze tender documents and manage tender-related information through a unified AI-powered platform.

Instead of using a single RAG pipeline for every question, the system uses a **multi-agent architecture** where each question is routed to the appropriate specialized agent.

```text
Database Question
       ↓
   SQL Agent

Document Question
       ↓
   RAG Agent

Report Request
       ↓
  Report Agent

Risk Question
       ↓
   Risk Agent

Comparison Request
       ↓
 Compare Agent
```

This architecture improves separation of responsibilities, maintainability, and extensibility.

---

# 👨‍💻 Development

For development:

```bash
docker compose up -d
```

FastAPI runs on:

```text
http://localhost:8000
```

Streamlit runs on:

```text
http://localhost:8501
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

---

# 📌 Important Design Principle

The `/chat` endpoint should execute the LangGraph workflow:

```text
ChatService
    ↓
graph.invoke()
    ↓
Supervisor
    ↓
Specialized Agent
```

It should **not directly call `RAGService.ask()` for every question**, otherwise database questions such as:

```text
how many tenders?
```

will incorrectly go through the RAG pipeline.

The Supervisor must decide the appropriate execution path.
