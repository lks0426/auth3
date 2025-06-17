# Development Guide

This document provides instructions for setting up and running the Auth System application in a development environment.

## Prerequisites

- Docker
- Docker Compose
- Node.js (version specified in `frontend/package.json`)
- Python (version specified in `backend/Dockerfile` or project docs)

## Local Setup

1.  **Clone the repository.**
2.  **Backend Setup:**
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate for Windows
    pip install -r requirements.txt -r requirements-dev.txt
    cp .env.example .env
    # Update .env with your local database settings if not using Docker for DB
    ```
3.  **Frontend Setup:**
    ```bash
    cd frontend
    npm install
    cp .env.example .env.local
    # Update .env.local if needed
    ```
4.  **Run `scripts/dev-setup.sh`** (This script may automate some of the above and start Docker services).
    Alternatively, to run with Docker Compose for services like database:
    ```bash
    docker-compose -f docker-compose.dev.yml up -d postgres_db redis # or similar
    ```
    Then run backend and frontend manually:
    - Backend: `uvicorn main:app --reload --port 8000` (from `backend/` dir)
    - Frontend: `npm run dev` (from `frontend/` dir)


## Running with Docker Compose (Development)

A `docker-compose.dev.yml` might be provided for a more integrated development experience.
```bash
docker-compose -f docker-compose.dev.yml up --build
```
This would typically run the backend, frontend (with HMR), and any necessary services like a database.

## Database Migrations (if applicable)

```bash
cd backend
alembic upgrade head
```
(Assuming Alembic is used for backend migrations)

## Running Tests

- **Backend:**
  ```bash
  cd backend
  pytest
  ```
- **Frontend:**
  ```bash
  cd frontend
  npm test
  # or specific lint/type-check commands
  npm run lint
  npm run type-check
  ```

## Code Style & Linting

<!-- Information about linters and formatters (e.g., Black, Flake8, ESLint, Prettier) -->
