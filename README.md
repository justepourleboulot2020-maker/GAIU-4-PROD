# GAIU 4 - Gestionnaire d'Automatisation des démarches Intelligentes pour Usagers

**Infrastructure d'automatisation administrative multi-agents avec IA**

Version 4.0 | Architecture Clean | Privacy-by-Design | RGPD Compliant

---

## 📋 Vue d'Ensemble

GAIU 4 est une plateforme complète d'automatisation des démarches administratives françaises utilisant une architecture multi-agents intelligents. Le système orchestre des agents spécialisés (Fiscal, Santé, Mobilité) pour gérer l'ensemble du cycle de vie des démarches administratives de manière sécurisée et conforme RGPD.

### Caractéristiques Principales

✅ **Multi-Agents Intelligence**
- Orchestrateur central avec State Machine
- Agents spécialisés par domaine (Fiscal, Santé, Mobilité, etc.)
- Distribution automatique des tâches selon l'expertise

✅ **Traitement Intelligent de Documents**
- OCR Vision (Claude API) pour extraction de données
- Parsing automatique selon le type de document
- Validation métier et mapping JSON structuré

✅ **Sécurité Maximale**
- Data Vault avec chiffrement AES-256-GCM
- Authentification FranceConnect+
- Séparation stricte données sensibles / métadonnées

✅ **Interface Utilisateur Moderne**
- Dashboard de contrôle temps réel
- Mode Urgence pour tâches critiques
- Timeline dynamique des événements
- Design minimaliste et responsive

---

## 🏗️ Architecture

### Stack Technologique

**Backend**
```
- Python 3.11+
- FastAPI (API REST)
- SQLAlchemy (ORM)
- PostgreSQL 15+ (Base de données)
- AsyncIO (Programmation asynchrone)
```

**Frontend**
```
- Next.js 14 (App Router)
- React 18
- TypeScript 5
- Tailwind CSS 3
- Lucide Icons
```

**Sécurité & IA**
```
- Cryptography (AES-256)
- Anthropic Claude API (Vision OCR)
- OAuth 2.0 / OpenID Connect
- FranceConnect+
```

### Architecture Layers

```
┌─────────────────────────────────────────────────┐
│            FRONTEND (Next.js)                    │
│  Dashboard | Urgence Mode | Timeline | Forms    │
└─────────────────────────────────────────────────┘
                      ↓ REST API
┌─────────────────────────────────────────────────┐
│              API LAYER (FastAPI)                 │
│  Routes | Middleware | Validation | Auth        │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│            CORE DOMAIN LAYER                     │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │ ORCHESTRATOR │←→│ STATE MACHINE│            │
│  └──────────────┘  └──────────────┘            │
│         ↓                                        │
│  ┌──────────────────────────────────────┐      │
│  │      SPECIALIZED AGENTS               │      │
│  │  Fiscal | Health | Mobility | ...    │      │
│  └──────────────────────────────────────┘      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│         INFRASTRUCTURE LAYER                     │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │   OCR    │  │   DATA   │  │   API    │     │
│  │ PIPELINE │  │  VAULT   │  │CONNECTORS│     │
│  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│          DATABASE (PostgreSQL)                   │
│  Users | Tasks | Documents | Audit Logs        │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Installation et Démarrage

### Prérequis

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose (optionnel)

### Installation Backend

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Éditer .env avec vos credentials

# Initialiser la base de données
python -m src.scripts.init_db

# Démarrer le serveur
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Installation Frontend

```bash
cd frontend

# Installer les dépendances
npm install
# ou
yarn install

# Configuration
cp .env.local.example .env.local
# Éditer .env.local

# Démarrer en développement
npm run dev
# ou
yarn dev

# Build production
npm run build
npm run start
```

### Installation avec Docker

```bash
# À la racine du projet
docker-compose up -d

# Les services seront disponibles sur:
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:3000
# - PostgreSQL: localhost:5432
```

---

## 📚 Guide d'Utilisation

### 1. Création d'une Tâche

```python
from src.core.orchestrator import Orchestrator, Task, AgentType, TaskPriority
from datetime import datetime, timedelta

orchestrator = Orchestrator()

# Créer une tâche fiscale
task = Task(
    user_id="user_123",
    title="Déclaration impôts 2025",
    description="Déclaration annuelle de revenus",
    agent_type=AgentType.FISCAL,
    priority=TaskPriority.HIGH,
    deadline=datetime.now() + timedelta(days=30),
    required_documents=["avis_imposition", "justificatif_revenus"]
)

# Soumettre à l'orchestrateur
created_task = await orchestrator.create_task(task)
```

### 2. Upload et Traitement de Documents

```python
from src.infrastructure.ingestion import DocumentParser, ClaudeVisionOCR, DocumentType

# Initialiser le parser
ocr = ClaudeVisionOCR(api_key="your_api_key")
parser = DocumentParser(ocr)

# Traiter un document
with open("avis_imposition.pdf", "rb") as f:
    document_data = f.read()

extracted = await parser.parse(
    document_data,
    DocumentType.AVIS_IMPOSITION
)

print(f"Champs extraits: {len(extracted.fields)}")
print(f"Confiance: {extracted.metadata.confidence_score:.2%}")
print(f"Données: {extracted.structured_data}")
```

### 3. Stockage Sécurisé

```python
from src.infrastructure.security import DataVault, DataClassification

vault = DataVault()

# Stocker des données sensibles
fiscal_data = {
    "numero_fiscal": "1234567890123",
    "revenus": 45000.00,
    "impot_du": 8540.00
}

record_id = vault.store(
    user_id="user_123",
    data=fiscal_data,
    data_type="fiscal",
    classification=DataClassification.SECRET
)

# Récupérer les données
retrieved = vault.retrieve(record_id, "user_123")
```

### 4. Connecteur API

```python
from src.infrastructure.connectors import ConnectorFactory, APICredentials, AuthMethod

# Créer un connecteur
credentials = APICredentials(
    auth_method=AuthMethod.OAUTH2,
    credentials={
        "client_id": "your_client_id",
        "client_secret": "your_secret"
    }
)

connector = ConnectorFactory.create("impots", credentials)
await connector.authenticate()

# Récupérer l'avis d'imposition
response = await connector.get_avis_imposition(
    numero_fiscal="1234567890123",
    reference_avis="REF2024",
    annee=2024
)
```

---

## 🔐 Sécurité

### Chiffrement

- **Algorithme**: AES-256-GCM (AEAD)
- **Gestion des clés**: Rotation automatique tous les 90 jours
- **Séparation**: Données sensibles dans le Data Vault, métadonnées en base

### Authentification

- **FranceConnect+**: Niveau d'authentification eidas2 (substantial)
- **OAuth 2.0 / OpenID Connect**
- **Sessions**: Expiration 2h, renouvellement automatique

### Conformité RGPD

✅ Privacy-by-Design
✅ Données minimales (pseudonymisation)
✅ Droit à l'effacement
✅ Portabilité des données
✅ Audit trail complet
✅ Retention policy automatique

---

## 📊 API Endpoints

### Authentication

```
POST   /auth/login              # Initier connexion FranceConnect
GET    /auth/callback           # Callback OAuth
POST   /auth/logout             # Déconnexion
GET    /auth/session            # Vérifier session
```

### Tasks

```
GET    /tasks                   # Liste des tâches
POST   /tasks                   # Créer une tâche
GET    /tasks/{id}              # Détails d'une tâche
PATCH  /tasks/{id}              # Mettre à jour
DELETE /tasks/{id}              # Annuler une tâche
GET    /tasks/{id}/status       # Statut en temps réel
```

### Documents

```
GET    /documents               # Liste des documents
POST   /documents/upload        # Upload document
GET    /documents/{id}          # Détails
DELETE /documents/{id}          # Supprimer
POST   /documents/{id}/attach   # Attacher à une tâche
```

### Users

```
GET    /users/me                # Profil utilisateur
PATCH  /users/me                # Mettre à jour profil
GET    /users/me/stats          # Statistiques
POST   /users/me/export         # Export RGPD
DELETE /users/me                # Supprimer compte
```

---

## 🧪 Tests

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=src

# Frontend tests
cd frontend
npm run test
npm run test:e2e

# Tests d'intégration
docker-compose -f docker-compose.test.yml up
pytest tests/integration/ -v
```

---

## 📦 Déploiement

### Variables d'Environnement

**Backend (.env)**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/gaiu4_db
SECRET_KEY=your_secret_key_here
ANTHROPIC_API_KEY=sk-ant-...
FRANCECONNECT_CLIENT_ID=your_fc_client_id
FRANCECONNECT_CLIENT_SECRET=your_fc_secret
FRANCECONNECT_REDIRECT_URI=https://yourdomain.com/auth/callback
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_ENVIRONMENT=production
```

### Production avec Kubernetes

```bash
# Build images
docker build -t gaiu4-backend:latest ./backend
docker build -t gaiu4-frontend:latest ./frontend

# Deploy to Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

---

## 🔧 Configuration

### Agents

Pour ajouter un nouvel agent spécialisé:

```python
from src.core.agents import BaseAgent, AgentType

class EmploymentAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.EMPLOYMENT)
        self.capabilities = [
            "contrat_travail",
            "fiche_paie",
            "demission"
        ]
    
    async def process_task(self, task: Task) -> Task:
        # Implémenter la logique métier
        pass
    
    async def validate_documents(self, task: Task) -> bool:
        # Validation spécifique
        pass
    
    async def submit_to_portal(self, task: Task) -> Dict[str, Any]:
        # Soumission API
        pass

# Enregistrement
from src.core.agents import AgentRegistry
AgentRegistry.register(EmploymentAgent())
```

### Connecteurs API

Pour ajouter un connecteur à un nouveau portail:

```python
from src.infrastructure.connectors import BaseAPIConnector

class CustomPortalConnector(BaseAPIConnector):
    def __init__(self, credentials):
        super().__init__(
            base_url="https://api.portal.gouv.fr",
            credentials=credentials
        )
    
    async def authenticate(self) -> bool:
        # Implémenter authentification
        pass
    
    async def test_connection(self) -> bool:
        # Test de connectivité
        pass

# Enregistrement
ConnectorFactory.register_connector("custom", CustomPortalConnector)
```

---

## 📈 Monitoring & Logs

### Logs

Les logs sont structurés en JSON avec les niveaux suivants:

- **DEBUG**: Informations détaillées pour le debugging
- **INFO**: Événements normaux (création tâche, transitions, etc.)
- **WARNING**: Situations anormales mais gérées
- **ERROR**: Erreurs nécessitant attention
- **CRITICAL**: Défaillances système

### Métriques

Métriques exposées sur `/metrics` (format Prometheus):

- `gaiu4_tasks_total`: Nombre total de tâches
- `gaiu4_tasks_by_state`: Tâches par état
- `gaiu4_tasks_by_agent`: Tâches par agent
- `gaiu4_ocr_confidence_avg`: Confiance OCR moyenne
- `gaiu4_api_response_time`: Temps de réponse API

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez suivre ces étapes:

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Standards de Code

- **Backend**: PEP 8, type hints obligatoires
- **Frontend**: ESLint + Prettier
- **Tests**: Couverture > 80%
- **Documentation**: Docstrings pour toutes les fonctions publiques

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 👥 Équipe

- **Architecture & Backend**: Claude (Anthropic)
- **Infrastructure**: Multi-Agent System Design
- **Frontend**: Next.js / React
- **Sécurité**: Data Vault & Encryption

---

## 📞 Support

Pour toute question ou problème:

- **Issues**: https://github.com/votre-org/gaiu4/issues
- **Documentation**: https://docs.gaiu4.app
- **Email**: support@gaiu4.app

---

## 🗺️ Roadmap

### Version 4.1 (Q2 2025)
- [ ] Agent Housing (logement)
- [ ] Agent Employment (emploi)
- [ ] Support multi-langue (EN, ES, DE)
- [ ] Application mobile (React Native)

### Version 4.2 (Q3 2025)
- [ ] IA Prédictive (anticipation des besoins)
- [ ] Assistant vocal
- [ ] Intégration blockchain pour certificats
- [ ] API publique pour partenaires

### Version 5.0 (Q4 2025)
- [ ] Architecture serverless complète
- [ ] Multi-tenancy
- [ ] Marketplace d'agents tiers
- [ ] Intelligence collective (apprentissage fédéré)

---

**GAIU 4** - Simplifier l'administration, un agent à la fois. 🚀
