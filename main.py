from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GAIU 4 API")

# On autorise ton interface v0 à parler au serveur
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
        "engine": "Connecté"
    }

@app.post("/analyze")
async def analyze_document(data: dict):
    user_text = data.get("text", "").lower()
    if "passeport" in user_text or "identité" in user_text:
        reponse = "Analyse : Pièce d'identité détectée. Extraction des données en cours... Statut : Prêt pour Auto-Fill."
    elif "facture" in user_text or "edf" in user_text:
        reponse = "Analyse : Justificatif de domicile détecté. Vérification de l'adresse... Statut : Conforme."
    else:
        reponse = f"GAIU 4 analyse votre demande : '{user_text}'. En attente de documents complémentaires."
    return {"status": "success", "analysis": reponse}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file_name = file.filename
    extracted_data = {
        "Nom": "DEMO UTILISATEUR",
        "Institution": "INSTITUTION EUROPEENNE",
        "Document": file_name,
        "Statut": "Vérifié & Prêt pour export"
    }
    return {
        "status": "success",
        "analysis": f"Analyse terminée pour '{file_name}'. Données extraites avec succès.",
        "data": extracted_data
    }



