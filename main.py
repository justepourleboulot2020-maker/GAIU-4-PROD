from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="GAIU 4 - Intelligence Artificielle")

# Configuration de la porte d'entrée (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURATION DU CERVEAU GAIU 4 ---
GAIU_PROMPT_SYSTEM = """
Tu es GAIU 4, l'IA spécialisée dans l'assistance administrative européenne.
Ta mission est d'analyser les documents avec une précision chirurgicale.
1. Identifie le type de document (Passeport, Facture, Attestation).
2. Extrais les données clés (Nom, Prénom, Dates, Numéros d'identification).
3. Vérifie la validité du document.
"""

@app.get("/")
async def root():
    return {
        "status": "online",
        "mode": "IA Gen Ready",
        "version": "4.0.1"
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file_name = file.filename
    
    # On simule ici ce que l'IA (Claude/GPT) renverrait 
    # une fois la clé API connectée dans les variables d'environnement.
    return {
        "status": "success",
        "analysis_report": {
            "agent": "GAIU 4",
            "document_detected": file_name,
            "extraction": {
                "nom_complet": "EXTRACTION IA EN COURS",
                "statut": "Analyse structurelle réussie"
            },
            "prompt_instructions": GAIU_PROMPT_SYSTEM.strip()
        }
    }

@app.post("/analyze")
async def quick_analyze(data: dict):
    user_text = data.get("text", "")
    return {
        "status": "success",
        "message": f"GAIU 4 a traité votre message : '{user_text}'"
    }



