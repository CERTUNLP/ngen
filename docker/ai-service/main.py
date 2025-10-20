from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()
classifier = pipeline("text-classification", model="bert-base-multilingual-cased")


class IncidentData(BaseModel):
    description: str
    assigned_team: str


@app.post("/analyze/")
def analyze_incident(data: IncidentData):
    analysis = classifier(data.description)
    result = analysis[0]
    # Podés implementar tu propia lógica:
    # comparar descripción con equipo asignado, sugerir cambios, etc.
    return {
        "input": data.dict(),
        "ai_suggestion": f"El modelo sugiere revisar la asignación al equipo {data.assigned_team}.",
        "model_output": result,
    }
