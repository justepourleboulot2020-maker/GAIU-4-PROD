"""
GAIU 4 - Orchestrateur Central Multi-Agents
Architecture: Clean Architecture + State Machine Pattern
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
from abc import ABC, abstractmethod
import uuid

# ============================================================================
# DOMAIN MODELS
# ============================================================================

class TaskState(Enum):
    """États du workflow des tâches administratives"""
    CREATED = "created"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_DOCUMENTS = "awaiting_documents"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Niveaux de priorité"""
    URGENT = "urgent"          # Mode urgence activé
    HIGH = "high"              # Échéance < 7 jours
    MEDIUM = "medium"          # Échéance < 30 jours
    LOW = "low"                # Échéance > 30 jours


class AgentType(Enum):
    """Types d'agents spécialisés"""
    FISCAL = "fiscal"
    HEALTH = "health"
    MOBILITY = "mobility"
    HOUSING = "housing"
    EMPLOYMENT = "employment"


@dataclass
class Task:
    """Entité métier: Tâche administrative"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    title: str = ""
    description: str = ""
    agent_type: AgentType = AgentType.FISCAL
    state: TaskState = TaskState.CREATED
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    required_documents: List[str] = field(default_factory=list)
    submitted_documents: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    
    def update_state(self, new_state: TaskState):
        """Met à jour l'état avec timestamp"""
        self.state = new_state
        self.updated_at = datetime.utcnow()
        
    def calculate_priority(self):
        """Calcule la priorité basée sur l'échéance"""
        if not self.deadline:
            return
        
        days_remaining = (self.deadline - datetime.utcnow()).days
        
        if days_remaining < 0:
            self.priority = TaskPriority.URGENT
        elif days_remaining <= 7:
            self.priority = TaskPriority.HIGH
        elif days_remaining <= 30:
            self.priority = TaskPriority.MEDIUM
        else:
            self.priority = TaskPriority.LOW


# ============================================================================
# STATE MACHINE
# ============================================================================

class StateTransition:
    """Définit les transitions autorisées entre états"""
    
    ALLOWED_TRANSITIONS: Dict[TaskState, List[TaskState]] = {
        TaskState.CREATED: [TaskState.PENDING, TaskState.CANCELLED],
        TaskState.PENDING: [TaskState.IN_PROGRESS, TaskState.CANCELLED],
        TaskState.IN_PROGRESS: [
            TaskState.AWAITING_DOCUMENTS,
            TaskState.UNDER_REVIEW,
            TaskState.COMPLETED,
            TaskState.FAILED,
            TaskState.CANCELLED
        ],
        TaskState.AWAITING_DOCUMENTS: [
            TaskState.IN_PROGRESS,
            TaskState.CANCELLED
        ],
        TaskState.UNDER_REVIEW: [
            TaskState.COMPLETED,
            TaskState.IN_PROGRESS,
            TaskState.FAILED
        ],
        TaskState.COMPLETED: [],
        TaskState.FAILED: [TaskState.PENDING],
        TaskState.CANCELLED: []
    }
    
    @classmethod
    def can_transition(cls, from_state: TaskState, to_state: TaskState) -> bool:
        """Vérifie si une transition est autorisée"""
        return to_state in cls.ALLOWED_TRANSITIONS.get(from_state, [])
    
    @classmethod
    def validate_transition(cls, task: Task, new_state: TaskState) -> bool:
        """Valide et applique une transition d'état"""
        if not cls.can_transition(task.state, new_state):
            raise ValueError(
                f"Transition invalide: {task.state.value} -> {new_state.value}"
            )
        
        task.update_state(new_state)
        return True


class StateMachine:
    """Machine à états pour gérer le cycle de vie des tâches"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def transition(self, task: Task, new_state: TaskState, 
                        context: Optional[Dict[str, Any]] = None) -> Task:
        """Effectue une transition d'état avec validation"""
        
        self.logger.info(
            f"Task {task.id}: {task.state.value} -> {new_state.value}"
        )
        
        # Validation
        StateTransition.validate_transition(task, new_state)
        
        # Callbacks pré-transition
        await self._pre_transition_hook(task, new_state, context)
        
        # Transition
        task.update_state(new_state)
        
        # Callbacks post-transition
        await self._post_transition_hook(task, context)
        
        return task
    
    async def _pre_transition_hook(self, task: Task, new_state: TaskState,
                                   context: Optional[Dict[str, Any]]):
        """Hook exécuté avant la transition"""
        
        # Vérifications spécifiques par état
        if new_state == TaskState.UNDER_REVIEW:
            if not task.submitted_documents:
                raise ValueError("Documents requis manquants")
        
        if new_state == TaskState.COMPLETED:
            task.progress = 100.0
    
    async def _post_transition_hook(self, task: Task, 
                                   context: Optional[Dict[str, Any]]):
        """Hook exécuté après la transition"""
        
        # Notifications, logs, événements
        if task.state == TaskState.COMPLETED:
            self.logger.info(f"Task {task.id} complétée avec succès")
        
        elif task.state == TaskState.FAILED:
            self.logger.error(
                f"Task {task.id} échouée: {task.error_message}"
            )


# ============================================================================
# AGENTS BASE
# ============================================================================

class BaseAgent(ABC):
    """Classe abstraite pour tous les agents spécialisés"""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"{__name__}.{agent_type.value}")
        self.capabilities: List[str] = []
    
    @abstractmethod
    async def process_task(self, task: Task) -> Task:
        """Traite une tâche et retourne la tâche mise à jour"""
        pass
    
    @abstractmethod
    async def validate_documents(self, task: Task) -> bool:
        """Valide les documents requis pour la tâche"""
        pass
    
    @abstractmethod
    async def submit_to_portal(self, task: Task) -> Dict[str, Any]:
        """Soumet la demande au portail administratif"""
        pass
    
    async def can_handle(self, task: Task) -> bool:
        """Vérifie si l'agent peut traiter cette tâche"""
        return task.agent_type == self.agent_type
    
    async def update_progress(self, task: Task, progress: float):
        """Met à jour la progression de la tâche"""
        task.progress = min(100.0, max(0.0, progress))
        task.updated_at = datetime.utcnow()


# ============================================================================
# ORCHESTRATOR
# ============================================================================

class Orchestrator:
    """
    Orchestrateur central du système GAIU 4
    Coordonne les agents et gère le workflow global
    """
    
    def __init__(self):
        self.state_machine = StateMachine()
        self.agents: Dict[AgentType, BaseAgent] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.logger = logging.getLogger(__name__)
        self.active_tasks: Dict[str, Task] = {}
        
    def register_agent(self, agent: BaseAgent):
        """Enregistre un agent spécialisé"""
        self.agents[agent.agent_type] = agent
        self.logger.info(f"Agent {agent.agent_type.value} enregistré")
    
    async def create_task(self, task: Task) -> Task:
        """Crée une nouvelle tâche et l'ajoute à la queue"""
        
        # Calcule la priorité automatiquement
        task.calculate_priority()
        
        # Transition vers PENDING
        await self.state_machine.transition(task, TaskState.PENDING)
        
        # Ajoute à la queue de traitement
        await self.task_queue.put(task)
        self.active_tasks[task.id] = task
        
        self.logger.info(
            f"Tâche créée: {task.id} ({task.priority.value})"
        )
        
        return task
    
    async def dispatch_task(self, task: Task) -> Task:
        """
        Distribue une tâche à l'agent approprié
        Cœur de la logique de dispatch multi-agents
        """
        
        # Trouve l'agent capable de traiter cette tâche
        agent = self.agents.get(task.agent_type)
        
        if not agent:
            task.error_message = f"Aucun agent pour {task.agent_type.value}"
            await self.state_machine.transition(task, TaskState.FAILED)
            return task
        
        if not await agent.can_handle(task):
            task.error_message = "Agent incompatible avec la tâche"
            await self.state_machine.transition(task, TaskState.FAILED)
            return task
        
        # Transition vers IN_PROGRESS
        await self.state_machine.transition(task, TaskState.IN_PROGRESS)
        
        try:
            # L'agent traite la tâche
            updated_task = await agent.process_task(task)
            
            self.logger.info(
                f"Tâche {task.id} traitée par {agent.agent_type.value}"
            )
            
            return updated_task
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement: {str(e)}")
            task.error_message = str(e)
            await self.state_machine.transition(task, TaskState.FAILED)
            return task
    
    async def process_queue(self):
        """
        Boucle principale de traitement des tâches
        Trie par priorité et dispatche aux agents
        """
        
        while True:
            try:
                # Récupère la tâche (avec timeout pour permettre l'arrêt)
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                
                # Dispatch à l'agent approprié
                await self.dispatch_task(task)
                
                # Marque la tâche comme traitée
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Erreur dans la queue: {str(e)}")
    
    async def get_task_status(self, task_id: str) -> Optional[Task]:
        """Récupère le statut d'une tâche"""
        return self.active_tasks.get(task_id)
    
    async def get_user_tasks(self, user_id: str, 
                           state: Optional[TaskState] = None) -> List[Task]:
        """Récupère toutes les tâches d'un utilisateur"""
        
        tasks = [
            task for task in self.active_tasks.values()
            if task.user_id == user_id
        ]
        
        if state:
            tasks = [task for task in tasks if task.state == state]
        
        # Trie par priorité puis date de création
        return sorted(
            tasks,
            key=lambda t: (
                t.priority.value,
                t.created_at
            ),
            reverse=True
        )
    
    async def cancel_task(self, task_id: str) -> bool:
        """Annule une tâche en cours"""
        
        task = self.active_tasks.get(task_id)
        if not task:
            return False
        
        try:
            await self.state_machine.transition(task, TaskState.CANCELLED)
            return True
        except ValueError:
            return False
    
    async def start(self):
        """Démarre l'orchestrateur"""
        self.logger.info("Orchestrateur GAIU 4 démarré")
        await self.process_queue()


# ============================================================================
# EXEMPLE D'UTILISATION
# ============================================================================

if __name__ == "__main__":
    
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Création de l'orchestrateur
    orchestrator = Orchestrator()
    
    # Les agents spécialisés seraient enregistrés ici
    # orchestrator.register_agent(FiscalAgent())
    # orchestrator.register_agent(HealthAgent())
    # orchestrator.register_agent(MobilityAgent())
    
    # Exemple de création de tâche
    task = Task(
        user_id="user_123",
        title="Déclaration impôts 2025",
        description="Déclaration de revenus annuelle",
        agent_type=AgentType.FISCAL,
        deadline=datetime(2025, 5, 31),
        required_documents=["avis_imposition", "justificatif_revenus"]
    )
    
    # Démarrage asynchrone
    # asyncio.run(orchestrator.create_task(task))
    # asyncio.run(orchestrator.start())
