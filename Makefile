.PHONY: api app all
all: api app

api:
	cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload

app:
	cd frontend && npm i && npm run dev
