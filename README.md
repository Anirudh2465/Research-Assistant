# Research OS

**Research OS** is an AI-powered workspace designed to turn chaotic research thoughts into defensible, high-quality projects. It acts as a "second brain" for researchers, integrating knowledge management, idea synthesis, project isolation, and execution tracking into a single closed-loop system.

## Features

- **Global Knowledge Graph**: Ingest papers (PDFs) and extract structured concepts using LLMs.
- **Idea Synthesis**: Generate novel research ideas using formal creativity modes (e.g., Cross-Domain Transfer, Assumption Violation).
- **Project Isolation**: Create scoped projects with their own knowledge graphs, preventing context contamination.
- **Execution Engine**: Track tasks with contexts, severity, and importance.
- **Visual Interface**: React-based frontend with "Three-Pane" deep work views and force-directed graph visualization.

## Prerequisites

- **Docker Desktop** (for Neo4j and Redis)
- **Python 3.10+**
- **Node.js 18+** & **npm**
- **Grobid** (Optional, for robust PDF parsing - typically runs in Docker)

## Installation

### 1. Backend Setup (using uv)

1.  Navigate to the project root:
    ```bash
    cd research-os
    ```

2.  Install `uv` (if not installed):
    ```bash
    pip install uv
    ```

3.  Sync dependencies:
    ```bash
    uv sync
    ```

4.  (Optional) Setup Auto-Activation:
    **Important:** Ensure you are in the `research-os` directory.
    ```bash
    cd research-os  # If not already there
    ./scripts/setup_auto_activate.ps1
    ```

5.  Configure Environment:
    - Copy the example environment file (if available) or create `.env`.
    - Ensure `OPENAI_API_KEY` (or your local LLM config) is set.
    - Ensure Neo4j credentials match `docker-compose.yml`.

### 2. Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

## Running the System

### 1. Start Infrastructure (Database & Services)

Start Neo4j, Redis, and Grobid using Docker:
```bash
docker-compose up -d
```

### 2. Start Backend

You can use the helper script (Git Bash/Linux) or run commands manually.

**Option A: Helper Script**
```bash
./scripts/start_all.sh
```

**Option B: Manual Start**
Terminal 1 (API):
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 (Celery Worker):
```bash
celery -A backend.workers.celery_app worker --loglevel=info -P solo
```
*(Note: `-P solo` is recommended for Windows)*

### 3. Start Frontend

```bash
cd frontend
npm run dev
```
Access the UI at: **http://localhost:5173**

## Usage Workflow

1.  **Ingest Knowledge**: Go to **Projects**, create a project, then upload papers in the "Papers" panel to populate the graph.
2.  **Explore**: Use the **Research** page to search the global knowledge graph.
3.  **Ideate**: Go to **Ideas**, click "New Idea", and select a synthesis mode (e.g., "Method Stacking").
4.  **Execute**: Promote mature ideas to Projects. Go to **Tasks** to schedule work based on Severity/Importance.

## Troubleshooting

- **Neo4j Connection Error**: Ensure Docker is running and the password in `.env` matches `docker-compose.yml` (Default: `password`).
- **PDF Parsing Fails**: Ensure the Grobid service is healthy (`localhost:8070`).
