# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MergeInvoice is a full-stack application for processing, managing, and merging invoices (PDF documents). It combines a Vue.js frontend with a Python FastAPI backend in a monorepo structure.

## Commands

### Frontend (root directory)
- `npm install` - Install dependencies
- `npm run dev` - Start Vite development server on port 5173
- `npm run build` - Type-check and build for production (runs type-check and build-only in parallel)
- `npm run build-only` - Build without type checking
- `npm run preview` - Preview production build locally
- `npm run type-check` - Run TypeScript type checking with vue-tsc
- `npm run format` - Format code with Prettier

### Backend (web/ directory)
- `pip install -r requirements.txt` - Install Python dependencies
- `python run.py` - Start the FastAPI server (recommended)
- `uvicorn main:app --reload` - Start with auto-reload for development
- `python main.py` - Alternative way to start the server
- Health check: `curl http://localhost:8000/health`

## Architecture

### Frontend (`src/`)
- **Vue 3 + TypeScript + Vite** with Pinia for state management and Vue Router
- **Styling**: Tailwind CSS with PostCSS
- **PDF rendering**: pdfjs-dist for client-side PDF handling
- API calls go through `/api` proxy to backend (configured in vite.config.ts)

Key directories:
- `api/` - API service layer (TypeScript clients for backend endpoints)
- `stores/` - Pinia state modules (invoice, user, layout)
- `views/` - Page components (HomePage, UploadPage, PreviewPage)
- `components/` - Reusable UI components

### Backend (`web/`)
- **FastAPI + SQLAlchemy + SQLite** with Pydantic for validation
- **MVT architecture** (Model-View-Template/Schema): models → schemas → services → views
- Database auto-initializes on startup via `init_db()` in main.py

Key directories:
- `app/models/` - SQLAlchemy ORM models (invoice, user, merge_task, draft)
- `app/schemas/` - Pydantic request/response schemas
- `app/services/` - Business logic (invoice_service, merge_service, minio_service, auth_service)
- `app/views/` - API endpoint controllers
- `app/database.py` - Database connection and initialization

External integrations:
- **MinIO** for object storage (required for file uploads)
- **WeChat OAuth** for authentication
- **pypdf/reportlab** for PDF manipulation and generation

## Development Setup

1. **Frontend**: Run `npm install` in root directory, then `npm run dev`
2. **Backend**:
   - Navigate to `web/` directory
   - Install dependencies: `pip install -r requirements.txt`
   - Copy `.env.example` to `.env` and configure environment variables
   - Start MinIO (required for file storage)
   - Run `python run.py`
3. **Verify**: Frontend at http://localhost:5173, Backend at http://localhost:8000, Health check at http://localhost:8000/health

## Development Notes

- Node.js requirement: ^20.19.0 or >=22.12.0
- Backend runs on port 8000, frontend dev server on port 5173
- Frontend proxies `/api` requests to backend
- SQLite database stored at `web/invoice.db` (auto-created on first run)
- Uploaded files stored in `web/uploads/` directory
- Environment variables configured via `web/.env` (see `web/.env.example`)
- MinIO must be running for file upload/download functionality
