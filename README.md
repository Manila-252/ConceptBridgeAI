# 🎓 ConceptBridge AI — Hackathon Repo

Fast, demo-ready scaffold with **backend/app** (FastAPI) and **frontend/src** (React + TS).

## Quickstart

```bash
# Terminal A (backend)
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload   # http://127.0.0.1:8000

# Terminal B (frontend)
cd frontend
npm i
npm run dev                    # http://127.0.0.1:5173
```

Or from the root:

```bash
make api
make app
```

## Structure

```
.
├─ backend/
│  ├─ app/
│  │  └─ main.py              # FastAPI app
│  ├─ requirements.txt
│  └─ Dockerfile
│
├─ frontend/
│  ├─ src/
│  │  ├─ App.tsx
│  │  └─ main.tsx
│  ├─ index.html
│  ├─ package.json
│  └─ tsconfig.json
│
├─ ml/
│  ├─ notebooks/
│  └─ models/                 # LFS-tracked (see .gitattributes)
│
├─ docs/
├─ .github/workflows/ci.yml
├─ .gitattributes
├─ .env.example
├─ Makefile
└─ LICENSE
```

## Endpoints (demo)

- `GET /` health
- `POST /echo { message }`
- `POST /predict { prompt }`
- `POST /assess { answer, rubric }`

## Team & Roles (fill in)

| Name | Role | Responsibilities |
| ---- | ---- | ---------------- |

| _Backend_+Integration | API/LLM orchestration | Endpoints, model calls, scoring |
| _Frontend_ | UI/UX | Screens, forms, API wiring |
| _ML_ | Modeling | Prompting, rubrics, evaluation |

## License

MIT
