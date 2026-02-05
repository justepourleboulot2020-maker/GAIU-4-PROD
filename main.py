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
from fastapi import UploadFile, File

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Ici, le moteur reçoit le vrai fichier
    file_name = file.filename
    file_extension = file_name.split(".")[-1].lower()
    
    # Logique de reconnaissance automatique du type de fichier
    if file_extension in ["jpg", "jpeg", "png"]:
        result = f"Document '{file_name}' reçu. Type : Image/Scan. Lancement de l'OCR GAIU..."
    elif file_extension == "pdf":
        result = f"Document '{file_name}' reçu. Type : PDF Officiel. Analyse des couches de texte..."
    else:
        result = f"Fichier '{file_name}' reçu. Format non identifié, analyse profonde requise."

    return {
        "status": "success",
        "filename": file_name,
        "analysis": result
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


