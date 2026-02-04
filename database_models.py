"""
GAIU 4 - Database Schema
PostgreSQL avec SQLAlchemy ORM
Privacy-by-design & RGPD compliant
"""

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean, 
    ForeignKey, Text, JSON, Enum, Index, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
import uuid


Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class UserStatus(PyEnum):
    """Statut du compte utilisateur"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"
    PENDING_VERIFICATION = "pending_verification"


class TaskStateEnum(PyEnum):
    """États des tâches"""
    CREATED = "created"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_DOCUMENTS = "awaiting_documents"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriorityEnum(PyEnum):
    """Priorités des tâches"""
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AgentTypeEnum(PyEnum):
    """Types d'agents"""
    FISCAL = "fiscal"
    HEALTH = "health"
    MOBILITY = "mobility"
    HOUSING = "housing"
    EMPLOYMENT = "employment"


class DocumentTypeEnum(PyEnum):
    """Types de documents"""
    AVIS_IMPOSITION = "avis_imposition"
    FEUILLE_SOINS = "feuille_soins"
    CARTE_GRISE = "carte_grise"
    JUSTIFICATIF_DOMICILE = "justificatif_domicile"
    BULLETIN_SALAIRE = "bulletin_salaire"
    PERMIS_CONDUIRE = "permis_conduire"
    CARTE_IDENTITE = "carte_identite"


class DataClassificationEnum(PyEnum):
    """Classification des données"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"


# ============================================================================
# MODELS
# ============================================================================

class User(Base):
    """
    Table des utilisateurs
    
    Privacy-by-design:
    - Données minimales stockées
    - Liaison FranceConnect via sub (pseudonyme)
    - Pas de stockage de données sensibles en clair
    """
    __tablename__ = "users"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # FranceConnect Identity
    fc_sub = Column(String(255), unique=True, nullable=False, index=True)
    
    # Données minimales (pseudonymisées)
    username = Column(String(100), unique=True, nullable=True)
    email_hash = Column(String(64), nullable=True)  # Hash SHA-256, pas l'email en clair
    
    # Status & Metadata
    status = Column(Enum(UserStatus), default=UserStatus.PENDING_VERIFICATION, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Preferences (non-sensible)
    preferences = Column(JSON, default={})
    
    # RGPD
    data_retention_until = Column(DateTime(timezone=True), nullable=True)
    consent_given_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    vault_records = relationship("VaultRecord", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_status', 'status'),
        Index('idx_user_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, fc_sub={self.fc_sub[:10]}...)>"


class Task(Base):
    """
    Table des tâches administratives
    """
    __tablename__ = "tasks"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Task Info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    agent_type = Column(Enum(AgentTypeEnum), nullable=False)
    
    # State Machine
    state = Column(Enum(TaskStateEnum), default=TaskStateEnum.CREATED, nullable=False)
    priority = Column(Enum(TaskPriorityEnum), default=TaskPriorityEnum.MEDIUM, nullable=False)
    
    # Progress
    progress = Column(Float, default=0.0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deadline = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata & Error Handling
    metadata = Column(JSON, default={})
    error_message = Column(Text, nullable=True)
    
    # Required vs Submitted Documents
    required_documents = Column(JSON, default=[])  # List of document types
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    documents = relationship("TaskDocument", back_populates="task", cascade="all, delete-orphan")
    state_transitions = relationship("TaskStateTransition", back_populates="task", cascade="all, delete-orphan")
    
    # Constraints & Indexes
    __table_args__ = (
        CheckConstraint('progress >= 0 AND progress <= 100', name='check_progress_range'),
        Index('idx_task_user', 'user_id'),
        Index('idx_task_state', 'state'),
        Index('idx_task_priority', 'priority'),
        Index('idx_task_deadline', 'deadline'),
        Index('idx_task_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, state={self.state.value})>"


class TaskStateTransition(Base):
    """
    Historique des transitions d'état (audit trail)
    """
    __tablename__ = "task_state_transitions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    
    from_state = Column(Enum(TaskStateEnum), nullable=True)  # NULL pour création
    to_state = Column(Enum(TaskStateEnum), nullable=False)
    
    transitioned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    transitioned_by = Column(String(50), default="system", nullable=False)  # "system" ou "user"
    
    context = Column(JSON, default={})  # Informations supplémentaires
    
    # Relationships
    task = relationship("Task", back_populates="state_transitions")
    
    __table_args__ = (
        Index('idx_transition_task', 'task_id'),
        Index('idx_transition_date', 'transitioned_at'),
    )


class Document(Base):
    """
    Table des documents uploadés
    
    Privacy:
    - Le contenu réel est dans le Data Vault (chiffré)
    - Ici on stocke uniquement les métadonnées
    """
    __tablename__ = "documents"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Document Info
    document_type = Column(Enum(DocumentTypeEnum), nullable=False)
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    page_count = Column(Integer, default=1)
    
    # Storage Reference
    vault_record_id = Column(String(64), nullable=False, unique=True)  # Référence au Data Vault
    
    # OCR & Extraction
    ocr_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    ocr_confidence = Column(Float, nullable=True)
    extracted_data = Column(JSON, default={})  # Données extraites (non-sensibles)
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Validation
    is_valid = Column(Boolean, default=False)
    validation_errors = Column(JSON, default=[])
    
    # Relationships
    user = relationship("User", back_populates="documents")
    task_documents = relationship("TaskDocument", back_populates="document", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_document_user', 'user_id'),
        Index('idx_document_type', 'document_type'),
        Index('idx_document_uploaded', 'uploaded_at'),
        Index('idx_document_vault', 'vault_record_id'),
    )
    
    def __repr__(self):
        return f"<Document(id={self.id}, type={self.document_type.value})>"


class TaskDocument(Base):
    """
    Table de liaison Many-to-Many entre Tasks et Documents
    """
    __tablename__ = "task_documents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    attached_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_required = Column(Boolean, default=True)
    
    # Relationships
    task = relationship("Task", back_populates="documents")
    document = relationship("Document", back_populates="task_documents")
    
    __table_args__ = (
        Index('idx_task_doc_task', 'task_id'),
        Index('idx_task_doc_document', 'document_id'),
    )


class VaultRecord(Base):
    """
    Références aux enregistrements du Data Vault
    (Le contenu chiffré est géré par le module security.py)
    """
    __tablename__ = "vault_records"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Key
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Vault Info
    vault_record_id = Column(String(64), unique=True, nullable=False, index=True)
    data_type = Column(String(50), nullable=False)  # fiscal, health, mobility
    classification = Column(Enum(DataClassificationEnum), nullable=False)
    
    # Metadata (non-sensible)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    accessed_at = Column(DateTime(timezone=True), nullable=True)
    access_count = Column(Integer, default=0)
    
    # RGPD
    retention_until = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="vault_records")
    
    __table_args__ = (
        Index('idx_vault_user', 'user_id'),
        Index('idx_vault_type', 'data_type'),
        Index('idx_vault_classification', 'classification'),
    )


class AuditLog(Base):
    """
    Journal d'audit pour traçabilité (RGPD Article 32)
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Who
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    actor_type = Column(String(20), nullable=False)  # user, system, admin, agent
    
    # What
    action = Column(String(100), nullable=False)  # create_task, upload_document, access_vault
    resource_type = Column(String(50), nullable=False)  # task, document, vault_record
    resource_id = Column(String(36), nullable=True)
    
    # When
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Where / How
    ip_address = Column(String(45), nullable=True)  # IPv4 ou IPv6
    user_agent = Column(String(255), nullable=True)
    
    # Details
    details = Column(JSON, default={})
    status = Column(String(20), default="success")  # success, failure, error
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    __table_args__ = (
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
    )


class APIConnector(Base):
    """
    Configuration des connecteurs API externes
    """
    __tablename__ = "api_connectors"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Connector Info
    name = Column(String(100), unique=True, nullable=False)
    connector_type = Column(String(50), nullable=False)  # impots, ameli, ants
    base_url = Column(String(255), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_health_check = Column(DateTime(timezone=True), nullable=True)
    health_status = Column(String(20), default="unknown")  # healthy, degraded, down
    
    # Configuration (chiffrée dans le vault)
    config_vault_id = Column(String(64), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_connector_type', 'connector_type'),
        Index('idx_connector_active', 'is_active'),
    )


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def create_all_tables(engine):
    """Crée toutes les tables dans la base de données"""
    Base.metadata.create_all(engine)
    print("✓ Tables créées avec succès")


def get_connection_string(
    host: str = "localhost",
    port: int = 5432,
    database: str = "gaiu4_db",
    username: str = "gaiu4_user",
    password: str = "secure_password"
) -> str:
    """Génère la string de connexion PostgreSQL"""
    
    return f"postgresql://{username}:{password}@{host}:{port}/{database}"


# ============================================================================
# EXEMPLE D'UTILISATION
# ============================================================================

if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Connexion à la base (à adapter selon votre environnement)
    connection_string = get_connection_string(
        host="localhost",
        database="gaiu4_dev",
        username="postgres",
        password="postgres"
    )
    
    # Création de l'engine
    engine = create_engine(
        connection_string,
        echo=True,  # Log SQL queries
        pool_size=10,
        max_overflow=20
    )
    
    # Création des tables
    create_all_tables(engine)
    
    # Session factory
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Exemple: Création d'un utilisateur
    user = User(
        fc_sub="fc_user_123456789",
        username="jean.dupont",
        email_hash=hashlib.sha256("jean.dupont@example.fr".encode()).hexdigest(),
        status=UserStatus.ACTIVE,
        consent_given_at=datetime.utcnow()
    )
    
    session.add(user)
    session.commit()
    
    print(f"Utilisateur créé: {user}")
    
    # Exemple: Création d'une tâche
    task = Task(
        user_id=user.id,
        title="Déclaration impôts 2025",
        description="Déclaration annuelle de revenus",
        agent_type=AgentTypeEnum.FISCAL,
        priority=TaskPriorityEnum.HIGH,
        required_documents=["avis_imposition", "justificatif_revenus"]
    )
    
    session.add(task)
    session.commit()
    
    print(f"Tâche créée: {task}")
    
    session.close()
