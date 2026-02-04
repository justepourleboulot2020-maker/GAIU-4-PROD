# GAIU 4 - Architecture Folder Tree

```
gaiu-4/
├── backend/
│   ├── src/
│   │   ├── core/
│   │   │   ├── orchestrator/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── orchestrator.py          # Orchestrateur central
│   │   │   │   ├── state_machine.py         # Machine à états
│   │   │   │   └── task_dispatcher.py       # Distribution des tâches
│   │   │   ├── agents/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_agent.py            # Classe abstraite
│   │   │   │   ├── fiscal_agent.py          # Agent fiscal
│   │   │   │   ├── health_agent.py          # Agent santé
│   │   │   │   ├── mobility_agent.py        # Agent mobilité
│   │   │   │   └── agent_registry.py        # Registre des agents
│   │   │   └── domain/
│   │   │       ├── entities/
│   │   │       │   ├── user_profile.py
│   │   │       │   ├── task.py
│   │   │       │   └── document.py
│   │   │       ├── repositories/
│   │   │       │   ├── user_repository.py
│   │   │       │   └── task_repository.py
│   │   │       └── services/
│   │   │           ├── encryption_service.py
│   │   │           └── auth_service.py
│   │   ├── infrastructure/
│   │   │   ├── ingestion/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ocr_processor.py         # OCR Vision
│   │   │   │   ├── document_parser.py       # Extraction données
│   │   │   │   └── data_mapper.py           # JSON mapping
│   │   │   ├── security/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── data_vault.py            # Coffre-fort
│   │   │   │   ├── encryption.py            # AES-256
│   │   │   │   └── france_connect.py        # FranceConnect+
│   │   │   ├── connectors/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_connector.py        # Connecteur universel
│   │   │   │   ├── impots_gouv_connector.py
│   │   │   │   ├── ameli_connector.py
│   │   │   │   └── ants_connector.py
│   │   │   └── database/
│   │   │       ├── __init__.py
│   │   │       ├── models.py                # Models SQLAlchemy
│   │   │       ├── migrations/
│   │   │       └── connection.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                      # FastAPI app
│   │   │   ├── routes/
│   │   │   │   ├── auth.py
│   │   │   │   ├── tasks.py
│   │   │   │   ├── documents.py
│   │   │   │   └── users.py
│   │   │   ├── middleware/
│   │   │   │   ├── auth_middleware.py
│   │   │   │   └── rate_limiter.py
│   │   │   └── schemas/
│   │   │       ├── task_schema.py
│   │   │       ├── user_schema.py
│   │   │       └── document_schema.py
│   │   └── config/
│   │       ├── __init__.py
│   │       ├── settings.py
│   │       └── logging_config.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   └── callback/
│   │   │   ├── (dashboard)/
│   │   │   │   ├── layout.tsx
│   │   │   │   ├── page.tsx                 # Dashboard principal
│   │   │   │   ├── tasks/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── documents/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── urgence/
│   │   │   │       └── page.tsx             # Mode urgence
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Badge.tsx
│   │   │   │   └── Timeline.tsx             # Timeline dynamique
│   │   │   ├── dashboard/
│   │   │   │   ├── StatusCard.tsx
│   │   │   │   ├── TaskList.tsx
│   │   │   │   └── ProgressBar.tsx
│   │   │   ├── documents/
│   │   │   │   ├── DocumentUploader.tsx
│   │   │   │   └── DocumentViewer.tsx
│   │   │   └── layout/
│   │   │       ├── Header.tsx
│   │   │       ├── Sidebar.tsx
│   │   │       └── Footer.tsx
│   │   ├── lib/
│   │   │   ├── api/
│   │   │   │   ├── client.ts
│   │   │   │   └── endpoints.ts
│   │   │   ├── hooks/
│   │   │   │   ├── useTasks.ts
│   │   │   │   ├── useAuth.ts
│   │   │   │   └── useDocuments.ts
│   │   │   └── utils/
│   │   │       ├── formatters.ts
│   │   │       └── validators.ts
│   │   ├── styles/
│   │   │   └── globals.css
│   │   └── types/
│   │       ├── task.ts
│   │       ├── user.ts
│   │       └── document.ts
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   └── tailwind.config.js
│
├── docs/
│   ├── architecture/
│   │   ├── system_design.md
│   │   ├── data_flow.md
│   │   └── security_model.md
│   ├── api/
│   │   └── openapi.yaml
│   └── deployment/
│       └── kubernetes/
│
├── scripts/
│   ├── setup_dev.sh
│   ├── migrations/
│   └── seed_data.py
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── .env.example
├── docker-compose.yml
└── README.md
```

## Architecture Layers

### 1. Core Domain Layer
- **Orchestrator**: Coordonne les agents et gère le workflow
- **Agents**: Spécialisés par domaine (Fiscal, Santé, Mobilité)
- **Entities**: Objets métier (User, Task, Document)

### 2. Infrastructure Layer
- **Ingestion**: OCR et extraction de données
- **Security**: Chiffrement et authentification
- **Connectors**: Adaptateurs pour portails administratifs
- **Database**: Persistance et migrations

### 3. API Layer
- **FastAPI**: REST API avec validation automatique
- **Routes**: Endpoints organisés par ressource
- **Middleware**: Authentification, rate limiting, CORS

### 4. Frontend Layer
- **Next.js 14**: App Router avec Server Components
- **Components**: UI réutilisables et composables
- **Hooks**: Logique réutilisable côté client
- **TypeScript**: Typage strict end-to-end

## Principes Architecturaux

1. **Clean Architecture**: Séparation claire des responsabilités
2. **Domain-Driven Design**: Logique métier au centre
3. **SOLID Principles**: Code maintenable et extensible
4. **Security by Design**: Chiffrement et auth natifs
5. **Scalability**: Microservices ready avec agents découplés
