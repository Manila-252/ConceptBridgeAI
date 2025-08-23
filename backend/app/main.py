from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="ConceptBridge AI API", version="0.1.0")

class Echo(BaseModel):
    message: str

class PredictIn(BaseModel):
    prompt: str

class AssessIn(BaseModel):
    answer: str
    rubric: str = "clarity, correctness, completeness"

@app.get("/")
def root():
    return {"ok": True, "service": "backend", "msg": "Hello from ConceptBridge API 👋"}

@app.post("/echo")
def echo(body: Echo):
    return {"echo": body.message}

@app.post("/predict")
def predict(body: PredictIn):
    snippet = f"Scenario for: {body.prompt}\nQuestion: Explain the core idea in 2 sentences."
    return {"simulation": snippet}

@app.post("/assess")
def assess(body: AssessIn):
    feedback = "Clear and mostly correct; add one concrete example."
    score = 0.8
    return {"score": score, "feedback": feedback}
