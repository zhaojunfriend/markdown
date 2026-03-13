# Markdown Editor

A full-stack Markdown editor with a **Vue 3** frontend and a **Python (FastAPI)** backend.

## Features

- ✏️ Split-pane editor — write Markdown on the left, see the rendered preview on the right
- 🔄 Live preview as you type (client-side rendering via `marked`)
- 💾 Save / load / delete Markdown files (stored server-side)
- 📋 File browser sidebar
- 🔒 Server-side HTML sanitisation via `bleach`

---

## Project Structure

```
markdown/
├── backend/          # Python FastAPI backend
│   ├── main.py
│   ├── requirements.txt
│   └── files/        # saved .md files (created at runtime)
└── frontend/         # Vue 3 + Vite frontend
    ├── src/
    │   ├── App.vue
    │   ├── main.js
    │   └── style.css
    ├── index.html
    └── vite.config.js
```

---

## Getting Started

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

> The Vite dev server proxies `/api` requests to `http://localhost:8000`, so no CORS configuration is needed during development.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/render` | Convert Markdown to sanitised HTML |
| `GET` | `/api/files` | List saved files |
| `POST` | `/api/files` | Save or overwrite a file |
| `GET` | `/api/files/{filename}` | Load file content |
| `DELETE` | `/api/files/{filename}` | Delete a file |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3, Vite, `marked` |
| Backend | Python 3, FastAPI, Uvicorn |
| Markdown rendering | `marked` (client), `markdown` + `bleach` (server) |
