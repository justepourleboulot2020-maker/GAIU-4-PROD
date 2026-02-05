from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="GAIU 4 - Intelligence Artificielle")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulation du branchement LLM (Claude/GPT)
# Ici, on prépare la place pour la clé API
API_KEY = os.getenv("AI_SERVICE_API_KEY", "MODE_DEMO")

@app.get("/")
async def root():
    return {"status": "online", "mode": "IA Gen Ready"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # 1. On récupère le fichier
    content = await file.read()
    file_name = file.filename
    
    # 2. Logique de l'IA Générative (Prompt Système)
    # Dans la version finale, ce texte sera envoyé à Claude ou GPT
    prompt_systeme = f"Tu es GAIU 4. Analyse le fichier {file_name} et extrais les entités administratives."
    
    # 3. Réponse simulée mais structurée comme une vraie IA
    return {
        "status": "success",
        "ai_analysis": {
            "document_type": "Détection automatique en cours...",
            "confidence_score": 0.98,
            "extracted_fields": {
                "nom": "Analyse via IA Gen...",
                "validite": "Vérification en cours..."
            },
            "system_prompt_used": prompt_systeme
        }
    }



