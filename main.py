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
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file_name = file.filename
    
    # Simulation d'extraction intelligente pour la démo
    extracted_data = {
        "Nom": "DEMO UTILISATEUR",
        "Institution": "CAF (Caisse d'Allocations Familiales)",
        "Document": file_name,
        "Statut": "Vérifié & Prêt pour export"
    }
    
    analysis_text = f"Analyse terminée pour '{file_name}'. L'IA a extrait les informations clés avec succès."

    return {
        "status": "success",
        "analysis": analysis_text,
        "data": extracted_data  # On envoie les données extraites ici !
    }
@app.post("/analyze")
async def analyze_document(data: dict):
    user_text = data.get("text", "").lower()
    
    # Simulation d'intelligence agentique
    if "passeport" in user_text or "identité" in user_text:
        reponse = "Analyse : Pièce d'identité détectée. Extraction des données en cours... Statut : Prêt pour Auto-Fill."
    elif "facture" in user_text or "edf" in user_text:
        reponse = "Analyse : Justificatif de domicile détecté. Vérification de l'adresse... Statut : Conforme."
    else:
        reponse = f"GAIU 4 analyse votre demande : '{user_text}'. En attente de documents complémentaires."

    return {
        "status": "success",
        "analysis": reponse
    }



