"""
GAIU 4 - Agents Spécialisés
Implémentations concrètes des agents métier
"""

from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime

from orchestrator import (
    BaseAgent, Task, TaskState, AgentType
)


# ============================================================================
# FISCAL AGENT
# ============================================================================

class FiscalAgent(BaseAgent):
    """
    Agent spécialisé dans les démarches fiscales
    - Déclaration de revenus
    - Avis d'imposition
    - Prélèvement à la source
    - Taxe d'habitation/foncière
    """
    
    def __init__(self):
        super().__init__(AgentType.FISCAL)
        self.capabilities = [
            "declaration_revenus",
            "avis_imposition",
            "prelevement_source",
            "taxe_habitation",
            "taxe_fonciere"
        ]
        self.portal_url = "https://www.impots.gouv.fr"
    
    async def process_task(self, task: Task) -> Task:
        """Traite une tâche fiscale"""
        
        self.logger.info(f"Traitement tâche fiscale: {task.title}")
        
        # Phase 1: Validation des documents
        await self.update_progress(task, 10.0)
        
        documents_valid = await self.validate_documents(task)
        
        if not documents_valid:
            from orchestrator import StateTransition, StateMachine
            state_machine = StateMachine()
            await state_machine.transition(task, TaskState.AWAITING_DOCUMENTS)
            return task
        
        await self.update_progress(task, 30.0)
        
        # Phase 2: Extraction et préparation des données
        fiscal_data = await self._extract_fiscal_data(task)
        task.metadata['fiscal_data'] = fiscal_data
        
        await self.update_progress(task, 50.0)
        
        # Phase 3: Pré-remplissage du formulaire
        form_data = await self._prepare_form_data(fiscal_data)
        task.metadata['form_data'] = form_data
        
        await self.update_progress(task, 70.0)
        
        # Phase 4: Soumission au portail
        from orchestrator import StateTransition, StateMachine
        state_machine = StateMachine()
        await state_machine.transition(task, TaskState.UNDER_REVIEW)
        
        submission_result = await self.submit_to_portal(task)
        task.metadata['submission'] = submission_result
        
        await self.update_progress(task, 90.0)
        
        # Phase 5: Finalisation
        if submission_result.get('success'):
            await state_machine.transition(task, TaskState.COMPLETED)
            task.metadata['confirmation_number'] = submission_result.get('reference')
        else:
            task.error_message = submission_result.get('error')
            await state_machine.transition(task, TaskState.FAILED)
        
        await self.update_progress(task, 100.0)
        
        return task
    
    async def validate_documents(self, task: Task) -> bool:
        """Valide les documents fiscaux requis"""
        
        required = set(task.required_documents)
        submitted = set(task.submitted_documents)
        
        missing = required - submitted
        
        if missing:
            self.logger.warning(f"Documents manquants: {missing}")
            task.metadata['missing_documents'] = list(missing)
            return False
        
        # Validation du contenu des documents
        for doc_id in task.submitted_documents:
            is_valid = await self._validate_document_content(doc_id)
            if not is_valid:
                self.logger.error(f"Document invalide: {doc_id}")
                return False
        
        return True
    
    async def _validate_document_content(self, doc_id: str) -> bool:
        """Valide le contenu d'un document (OCR + règles métier)"""
        
        # Simulation - serait connecté au module OCR
        await asyncio.sleep(0.1)
        
        # Vérifications:
        # - Format valide
        # - Données extraites cohérentes
        # - Date de validité
        
        return True
    
    async def _extract_fiscal_data(self, task: Task) -> Dict[str, Any]:
        """Extrait les données fiscales des documents"""
        
        # Simulation d'extraction OCR
        await asyncio.sleep(0.2)
        
        return {
            "revenus_annuels": 45000.00,
            "charges_deductibles": 3500.00,
            "nombre_parts": 2.0,
            "situation_familiale": "marie",
            "nombre_enfants": 1,
            "annee_fiscale": 2024
        }
    
    async def _prepare_form_data(self, fiscal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare les données pour le formulaire administratif"""
        
        return {
            "form_type": "2042",
            "fields": {
                "1AJ": fiscal_data.get("revenus_annuels"),
                "6DD": fiscal_data.get("charges_deductibles"),
                "V": fiscal_data.get("nombre_parts")
            },
            "annexes": []
        }
    
    async def submit_to_portal(self, task: Task) -> Dict[str, Any]:
        """Soumet la déclaration au portail impots.gouv.fr"""
        
        # Simulation - utiliserait le connector API
        await asyncio.sleep(0.5)
        
        return {
            "success": True,
            "reference": f"DECL2025-{task.id[:8].upper()}",
            "submitted_at": datetime.utcnow().isoformat(),
            "status": "accepted",
            "portal_url": self.portal_url
        }


# ============================================================================
# HEALTH AGENT
# ============================================================================

class HealthAgent(BaseAgent):
    """
    Agent spécialisé dans les démarches de santé
    - Remboursements CPAM
    - Carte Vitale
    - Affiliation mutuelle
    - Arrêts maladie
    """
    
    def __init__(self):
        super().__init__(AgentType.HEALTH)
        self.capabilities = [
            "remboursement_cpam",
            "carte_vitale",
            "mutuelle",
            "arret_maladie",
            "prise_en_charge"
        ]
        self.portal_url = "https://www.ameli.fr"
    
    async def process_task(self, task: Task) -> Task:
        """Traite une tâche santé"""
        
        self.logger.info(f"Traitement tâche santé: {task.title}")
        
        await self.update_progress(task, 15.0)
        
        # Validation documents médicaux
        if not await self.validate_documents(task):
            from orchestrator import StateTransition, StateMachine
            state_machine = StateMachine()
            await state_machine.transition(task, TaskState.AWAITING_DOCUMENTS)
            return task
        
        await self.update_progress(task, 40.0)
        
        # Extraction données médicales
        health_data = await self._extract_health_data(task)
        task.metadata['health_data'] = health_data
        
        await self.update_progress(task, 60.0)
        
        # Calcul remboursement
        reimbursement = await self._calculate_reimbursement(health_data)
        task.metadata['reimbursement'] = reimbursement
        
        await self.update_progress(task, 80.0)
        
        # Soumission
        from orchestrator import StateTransition, StateMachine
        state_machine = StateMachine()
        await state_machine.transition(task, TaskState.UNDER_REVIEW)
        
        result = await self.submit_to_portal(task)
        
        if result.get('success'):
            await state_machine.transition(task, TaskState.COMPLETED)
        else:
            task.error_message = result.get('error')
            await state_machine.transition(task, TaskState.FAILED)
        
        await self.update_progress(task, 100.0)
        
        return task
    
    async def validate_documents(self, task: Task) -> bool:
        """Valide les documents médicaux"""
        
        await asyncio.sleep(0.1)
        
        # Vérifications spécifiques santé:
        # - Feuilles de soins
        # - Prescriptions
        # - Factures
        
        return len(task.submitted_documents) >= len(task.required_documents)
    
    async def _extract_health_data(self, task: Task) -> Dict[str, Any]:
        """Extrait les données médicales"""
        
        return {
            "type_acte": "consultation_specialiste",
            "montant_total": 150.00,
            "date_soin": "2025-02-01",
            "prescripteur": "Dr. Martin",
            "numero_securite_sociale": "1234567890123"
        }
    
    async def _calculate_reimbursement(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule le remboursement CPAM + mutuelle"""
        
        montant = health_data.get("montant_total", 0.0)
        
        # Taux de remboursement CPAM (70% pour spécialiste)
        cpam_rate = 0.70
        cpam_amount = montant * cpam_rate
        
        # Mutuelle complète (30%)
        mutuelle_rate = 0.30
        mutuelle_amount = montant * mutuelle_rate
        
        return {
            "montant_initial": montant,
            "cpam": {
                "taux": cpam_rate,
                "montant": cpam_amount
            },
            "mutuelle": {
                "taux": mutuelle_rate,
                "montant": mutuelle_amount
            },
            "reste_a_charge": 0.00
        }
    
    async def submit_to_portal(self, task: Task) -> Dict[str, Any]:
        """Soumet au portail Ameli"""
        
        await asyncio.sleep(0.4)
        
        return {
            "success": True,
            "reference": f"RBT-{task.id[:8].upper()}",
            "submitted_at": datetime.utcnow().isoformat(),
            "estimated_payment_date": "2025-02-15"
        }


# ============================================================================
# MOBILITY AGENT
# ============================================================================

class MobilityAgent(BaseAgent):
    """
    Agent spécialisé dans les démarches de mobilité
    - Permis de conduire
    - Carte grise
    - Contrôle technique
    - Amendes
    """
    
    def __init__(self):
        super().__init__(AgentType.MOBILITY)
        self.capabilities = [
            "permis_conduire",
            "carte_grise",
            "controle_technique",
            "amendes",
            "certificat_immatriculation"
        ]
        self.portal_url = "https://www.ants.gouv.fr"
    
    async def process_task(self, task: Task) -> Task:
        """Traite une tâche mobilité"""
        
        self.logger.info(f"Traitement tâche mobilité: {task.title}")
        
        await self.update_progress(task, 20.0)
        
        # Validation documents véhicule
        if not await self.validate_documents(task):
            from orchestrator import StateTransition, StateMachine
            state_machine = StateMachine()
            await state_machine.transition(task, TaskState.AWAITING_DOCUMENTS)
            return task
        
        await self.update_progress(task, 50.0)
        
        # Extraction données véhicule
        vehicle_data = await self._extract_vehicle_data(task)
        task.metadata['vehicle_data'] = vehicle_data
        
        await self.update_progress(task, 70.0)
        
        # Vérification éligibilité
        is_eligible = await self._check_eligibility(vehicle_data)
        
        if not is_eligible:
            task.error_message = "Non éligible pour cette démarche"
            from orchestrator import StateTransition, StateMachine
            state_machine = StateMachine()
            await state_machine.transition(task, TaskState.FAILED)
            return task
        
        await self.update_progress(task, 85.0)
        
        # Soumission
        from orchestrator import StateTransition, StateMachine
        state_machine = StateMachine()
        await state_machine.transition(task, TaskState.UNDER_REVIEW)
        
        result = await self.submit_to_portal(task)
        
        if result.get('success'):
            await state_machine.transition(task, TaskState.COMPLETED)
        else:
            task.error_message = result.get('error')
            await state_machine.transition(task, TaskState.FAILED)
        
        await self.update_progress(task, 100.0)
        
        return task
    
    async def validate_documents(self, task: Task) -> bool:
        """Valide les documents véhicule"""
        
        await asyncio.sleep(0.1)
        
        # Vérifications:
        # - Carte grise
        # - Permis de conduire
        # - Contrôle technique
        # - Assurance
        
        return True
    
    async def _extract_vehicle_data(self, task: Task) -> Dict[str, Any]:
        """Extrait les données du véhicule"""
        
        return {
            "immatriculation": "AB-123-CD",
            "marque": "Renault",
            "modele": "Clio",
            "annee": 2020,
            "vin": "VF1RJ0CODA123456",
            "puissance_fiscale": 5
        }
    
    async def _check_eligibility(self, vehicle_data: Dict[str, Any]) -> bool:
        """Vérifie l'éligibilité pour la démarche"""
        
        # Exemple: véhicule de moins de 10 ans
        current_year = datetime.now().year
        vehicle_age = current_year - vehicle_data.get("annee", 0)
        
        return vehicle_age < 10
    
    async def submit_to_portal(self, task: Task) -> Dict[str, Any]:
        """Soumet au portail ANTS"""
        
        await asyncio.sleep(0.3)
        
        return {
            "success": True,
            "reference": f"ANTS-{task.id[:8].upper()}",
            "submitted_at": datetime.utcnow().isoformat(),
            "processing_time": "48h",
            "tracking_url": f"{self.portal_url}/track/{task.id}"
        }


# ============================================================================
# AGENT REGISTRY
# ============================================================================

class AgentRegistry:
    """Registre centralisé des agents disponibles"""
    
    _agents: Dict[AgentType, BaseAgent] = {}
    
    @classmethod
    def register(cls, agent: BaseAgent):
        """Enregistre un agent"""
        cls._agents[agent.agent_type] = agent
        logging.info(f"Agent {agent.agent_type.value} registered")
    
    @classmethod
    def get_agent(cls, agent_type: AgentType) -> Optional[BaseAgent]:
        """Récupère un agent par type"""
        return cls._agents.get(agent_type)
    
    @classmethod
    def get_all_agents(cls) -> List[BaseAgent]:
        """Retourne tous les agents enregistrés"""
        return list(cls._agents.values())
    
    @classmethod
    def initialize_default_agents(cls):
        """Initialize les agents par défaut du système"""
        cls.register(FiscalAgent())
        cls.register(HealthAgent())
        cls.register(MobilityAgent())
        
        logging.info(f"Initialized {len(cls._agents)} agents")


# ============================================================================
# USAGE
# ============================================================================

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO)
    
    # Initialize tous les agents
    AgentRegistry.initialize_default_agents()
    
    # Exemple d'utilisation
    fiscal_agent = AgentRegistry.get_agent(AgentType.FISCAL)
    print(f"Agent fiscal capabilities: {fiscal_agent.capabilities}")
