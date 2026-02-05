from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# On importe ton fichier orchestrator (sans le .py)
try:
    import orchestrator
except ImportError:
    # Si le fichier est dans un sous-dossier ou nommé différemment
    orchestrator = None

app = FastAPI(title="GAIU 4 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "online", 
        "message": "GAIU 4 est operationnel",
        "engine": "Orchestrator chargé" if orchestrator else "Orchestrator en attente"
    }
@app.post("/analyze")
async def analyze_document(data: dict):
    # C'est ici que l'IA va travailler plus tard
    user_input = data.get("text", "")
    return {
        "status": "success",
        "analysis": f"GAIU 4 a reçu votre demande : '{user_input}'. Le moteur d'analyse est prêt."
    }

