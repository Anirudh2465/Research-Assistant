# Research OS

**Research OS** is an AI-powered workspace designed to turn chaotic research thoughts into defensible, high-quality projects. It acts as a "second brain" for researchers, integrating knowledge management, idea synthesis, project isolation, and execution tracking into a single closed-loop system.

---

## 🏗️ Architecture & Technologies

The codebase is structured as a robust, asynchronous web application leveraging multiple databases to separate operational state from connected knowledge.

- **Frontend (UI)**: React 18, Vite, Tailwind CSS, Lucide Icons, and React Force Graph (for knowledge graph visualization).
- **Backend (API)**: FastAPI with Pydantic for validation.
- **Relational DB (State)**: SQLite (via SQLAlchemy) for managing Projects, Tasks, and operational Idea metadata.
- **Graph DB (Knowledge)**: Neo4j for the true Knowledge Graph (Concepts, Assumptions, Limitations, Idea lineages).
- **Worker Queue (Async)**: Celery + Redis for heavy, long-running processes (PDF ingestion, LLM calls).
- **PDF Extraction**: Grobid (running in Docker) for high-accuracy scientific PDF parsing.
- **LLM Integration**: OpenAI-compatible endpoint support (easily swap between local models via LMStudio/Ollama or cloud APIs).

---

## 🚀 Features

- **Global Knowledge Graph**: Ingest papers (PDFs) via Celery workers, extract structured concepts using LLMs, and write them into Neo4j.
- **Idea Synthesis**: Generate novel research ideas using formal creativity modes (e.g., Cross-Domain Transfer, Assumption Violation) powered by LLM reasoning.
- **Project Isolation**: Create scoped projects with their own knowledge graphs, preventing context contamination.
- **Execution Engine**: Track execution tasks with severity and importance dimensions.
- **Visual Interface**: React-based frontend with force-directed graph visualizations and deep work views.

---

## 🛠️ Prerequisites

To run Research OS locally, you need:

1. **Docker & Docker Compose** (for Neo4j, Redis, and Grobid)
2. **Python 3.10+** (Backend & Workers)
3. **Node.js 18+** & **npm** (Frontend)
4. **uv** (for fast Python dependency management - install via `pip install uv`)

---

## ⚙️ Setting Up the Environment

### 1. Backend Dependencies

Navigate to the project root and use `uv` to install the backend dependencies. This will automatically create and populate a `.venv` folder.

```bash
uv sync
```

*(Alternatively, you can create a virtual environment manually and run `pip install -e .`)*

### 2. Environment Variables (.env)

Research OS uses `pydantic-settings` to manage configuration. You can configure the system by creating a `.env` file in the **root** of the project (where `backend/` lives).

Here is an example `.env` file:

```env
# API
API_HOST=127.0.0.1
API_PORT=8000

# Redis (Broker & Result Backend)
REDIS_URL=redis://localhost:6379/0
CELERY_BACKEND=redis://localhost:6379/1

# Neo4j Graph DB
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# LLM Configuration (Default is setup for a local OpenAI-compatible endpoint like LMStudio)
LLM_BASE_URL=http://localhost:1234/v1
LLM_API_KEY=local-llm
LLM_MODEL=openai-oss-20b
```

### 3. Frontend Dependencies

Navigate to the `frontend` folder and install the NPM dependencies:

```bash
cd frontend
npm install
```

---

## 🚦 Running the System

To run the full stack, you need to start 4 separate components. It is highly recommended to run these in separate terminal windows/tabs so you can monitor their logs.

### Terminal 1: Infrastructure (Docker)

Start Neo4j, Redis, and Grobid using the provided Docker Compose file from the project root:

```bash
docker-compose up -d
```
*(Wait a few moments for the Neo4j database and Grobid service to fully initialize.)*

### Terminal 2: FastAPI Backend Server

Activate the virtual environment and start the FastAPI web server from the project root:

```bash
# On Windows
.venv\Scripts\activate
# On Mac/Linux: source .venv/bin/activate

uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 3: Celery Background Worker

Activate the virtual environment and start the Celery worker to process PDF ingestion and graph tasks:

```bash
# On Windows
.venv\Scripts\activate
# On Mac/Linux: source .venv/bin/activate

# Use -P solo on Windows to avoid process spawning issues
celery -A backend.workers.celery_app worker --loglevel=info -P solo
```

### Terminal 4: React Frontend

Start the Vite development server for the UI:

```bash
cd frontend
npm run dev
```

---

## 🎯 Usage Workflow

Once all services are running, open your browser and navigate to **http://localhost:5173**.

1. **Ingest Knowledge**: 
   - Go to **Projects**, create a new project (e.g., "Efficient Diffusion Sampling").
   - Open the Project Workspace and upload scientific PDFs in the "Papers" panel.
   - The Celery worker will parse the PDF (via Grobid), extract concepts (via LLM), and populate the Knowledge Graph.
2. **Explore**: 
   - Use the **Research** page to search the global knowledge graph and view concept relationships.
3. **Ideate**: 
   - Go to **Ideas**, click "New Idea", select source concepts, and pick a synthesis mode.
   - Wait for the LLM to synthesize the idea and write the lineage into Neo4j.
4. **Execute**: 
   - Review Draft Ideas in the Idea detail page. Mark them as "Mature" and then "Promote" them to isolate them into their own Projects.
   - Go to **Tasks** to schedule execution work based on Severity/Importance.

---

## 🔧 Troubleshooting

- **Database Errors on Startup**: Ensure `docker-compose up -d` was successful. Check `docker ps` to verify Neo4j and Redis are running. 
- **Tasks Remaining Queued**: Make sure your Celery worker (Terminal 3) is running and pointing to the correct `REDIS_URL`. If on Windows, ensure you are using the `-P solo` flag.
- **LLM/Synthesis Failing**: Verify that your `LLM_BASE_URL` is pointing to an active, running local model (like LMStudio or Ollama) or that you have updated `.env` with a real OpenAI API Key.
- **PDF Upload Fails to Parse**: Ensure the Grobid container is healthy and responding on `localhost:8070`.
