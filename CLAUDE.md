# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MergeInvoice is a full-stack application for processing, managing, and merging invoices (PDF documents). It combines a Vue.js frontend with a Python FastAPI backend in a monorepo structure.

## Commands

### Frontend (root directory)
- `npm run dev` - Start Vite development server
- `npm run build` - Type-check and build for production
- `npm run type-check` - Run TypeScript type checking with vue-tsc
- `npm run format` - Format code with Prettier

### Backend (web/ directory)
- `pip install -r requirements.txt` - Install Python dependencies
- `python run.py` or `uvicorn main:app` - Start the FastAPI server

## Architecture

### Frontend (`src/`)
- **Vue 3 + TypeScript + Vite** with Pinia for state management and Vue Router
- **Styling**: Tailwind CSS
- **PDF rendering**: pdfjs-dist for client-side PDF handling
- API calls go through `/api` proxy to backend (configured in vite.config.ts)

Key directories:
- `api/` - API service layer (TypeScript clients for backend endpoints)
- `stores/` - Pinia state modules (invoice, user, layout)
- `views/` - Page components (HomePage, UploadPage, PreviewPage)
- `components/` - Reusable UI components

### Backend (`web/`)
- **FastAPI + SQLAlchemy + SQLite** with Pydantic for validation
- Layered architecture: models → schemas → services → views

Key directories:
- `app/models/` - SQLAlchemy ORM models (invoice, user, merge_task, draft)
- `app/schemas/` - Pydantic request/response schemas
- `app/services/` - Business logic (invoice_service, merge_service, minio_service, auth_service)
- `app/views/` - API endpoint controllers

External integrations:
- **MinIO** for object storage
- **WeChat OAuth** for authentication
- **pypdf/reportlab** for PDF manipulation and generation

## Development Notes

- Node.js requirement: ^20.19.0 or >=22.12.0
- Backend runs on port 8000, frontend dev server proxies `/api` requests to it
- SQLite database stored at `web/invoice.db`
- Environment variables configured via `web/.env` (see `web/.env.example`)
