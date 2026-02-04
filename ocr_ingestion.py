"""
GAIU 4 - Pipeline d'Ingestion de Documents
OCR + Extraction + Mapping vers JSON structuré
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import json
import base64
from abc import ABC, abstractmethod


# ============================================================================
# DOMAIN MODELS
# ============================================================================

class DocumentType(Enum):
    """Types de documents administratifs"""
    AVIS_IMPOSITION = "avis_imposition"
    FEUILLE_SOINS = "feuille_soins"
    CARTE_GRISE = "carte_grise"
    JUSTIFICATIF_DOMICILE = "justificatif_domicile"
    BULLETIN_SALAIRE = "bulletin_salaire"
    PERMIS_CONDUIRE = "permis_conduire"
    CARTE_IDENTITE = "carte_identite"
    CONTRAT_TRAVAIL = "contrat_travail"
    FACTURE = "facture"


@dataclass
class DocumentMetadata:
    """Métadonnées extraites du document"""
    document_id: str
    document_type: DocumentType
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
    file_size: int = 0
    mime_type: str = ""
    page_count: int = 1
    language: str = "fr"
    confidence_score: float = 0.0
    

@dataclass
class ExtractedField:
    """Champ extrait avec son niveau de confiance"""
    field_name: str
    value: Any
    confidence: float
    source_location: Optional[Tuple[int, int, int, int]] = None  # x, y, width, height
    

@dataclass
class ExtractedDocument:
    """Document après extraction complète"""
    metadata: DocumentMetadata
    fields: List[ExtractedField]
    raw_text: str = ""
    structured_data: Dict[str, Any] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    

# ============================================================================
# OCR PROCESSOR
# ============================================================================

class OCREngine(ABC):
    """Interface pour les moteurs OCR"""
    
    @abstractmethod
    async def extract_text(self, image_data: bytes) -> str:
        """Extrait le texte d'une image"""
        pass
    
    @abstractmethod
    async def extract_structured_data(self, image_data: bytes) -> Dict[str, Any]:
        """Extrait des données structurées (tableaux, champs)"""
        pass


class ClaudeVisionOCR(OCREngine):
    """
    OCR utilisant Claude Vision API
    Optimal pour documents administratifs français
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        
    async def extract_text(self, image_data: bytes) -> str:
        """Extrait le texte via Claude Vision"""
        
        # Simulation - en production, appel à l'API Anthropic
        # avec le document en base64
        
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Exemple de prompt structuré
        prompt = """
        Extrais le texte complet de ce document administratif français.
        Préserve la structure et la mise en forme.
        Identifie les sections importantes.
        """
        
        # Simulation de réponse
        extracted_text = """
        DIRECTION GÉNÉRALE DES FINANCES PUBLIQUES
        AVIS D'IMPÔT SUR LES REVENUS
        
        Année fiscale: 2024
        Numéro fiscal: 1234567890123
        
        Contribuable: DUPONT Jean
        Adresse: 123 Rue de la République, 75001 PARIS
        
        REVENUS DÉCLARÉS
        Salaires et traitements: 45 000,00 €
        Revenus fonciers: 12 000,00 €
        Total des revenus: 57 000,00 €
        
        IMPÔT CALCULÉ
        Revenu imposable: 52 000,00 €
        Impôt dû: 8 540,00 €
        """
        
        return extracted_text
    
    async def extract_structured_data(self, image_data: bytes) -> Dict[str, Any]:
        """Extrait des données structurées avec Vision"""
        
        # En production: appel API avec instructions spécifiques
        
        prompt = """
        Analyse ce document et extrait les données dans ce format JSON:
        {
            "type": "type de document",
            "dates": ["liste des dates trouvées"],
            "montants": ["montants avec devise"],
            "identifiants": ["numéros officiels"],
            "personnes": ["noms et prénoms"],
            "adresses": ["adresses complètes"]
        }
        """
        
        # Simulation
        return {
            "type": "avis_imposition",
            "dates": ["2024"],
            "montants": ["45000.00 EUR", "12000.00 EUR", "8540.00 EUR"],
            "identifiants": ["1234567890123"],
            "personnes": ["DUPONT Jean"],
            "adresses": ["123 Rue de la République, 75001 PARIS"]
        }


# ============================================================================
# DOCUMENT PARSER
# ============================================================================

class DocumentParser:
    """
    Parse les documents selon leur type
    Applique des règles métier spécifiques
    """
    
    # Patterns de regex pour extraction
    PATTERNS = {
        "date": r'\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})\b',
        "montant": r'(\d{1,3}(?:\s?\d{3})*(?:[,\.]\d{2})?)\s*€?',
        "numero_fiscal": r'\b(\d{13})\b',
        "immatriculation": r'\b([A-Z]{2}[-\s]?\d{3}[-\s]?[A-Z]{2})\b',
        "numero_secu": r'\b([12]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2})\b',
        "iban": r'\b([A-Z]{2}\d{2}\s?(?:\d{4}\s?){4,7}\d{1,4})\b',
        "siret": r'\b(\d{3}\s?\d{3}\s?\d{3}\s?\d{5})\b'
    }
    
    def __init__(self, ocr_engine: OCREngine):
        self.ocr = ocr_engine
    
    async def parse(self, document_data: bytes, 
                   document_type: DocumentType) -> ExtractedDocument:
        """Parse un document complet"""
        
        # Extraction OCR
        raw_text = await self.ocr.extract_text(document_data)
        structured_ocr = await self.ocr.extract_structured_data(document_data)
        
        # Métadonnées
        metadata = DocumentMetadata(
            document_id=self._generate_document_id(),
            document_type=document_type,
            file_size=len(document_data),
            confidence_score=0.95
        )
        
        # Extraction des champs selon le type
        fields = await self._extract_fields_by_type(
            raw_text, 
            structured_ocr,
            document_type
        )
        
        # Construction du document extrait
        extracted = ExtractedDocument(
            metadata=metadata,
            fields=fields,
            raw_text=raw_text,
            structured_data=self._build_structured_data(fields)
        )
        
        # Validation
        extracted.validation_errors = self._validate(extracted)
        
        return extracted
    
    async def _extract_fields_by_type(self, 
                                     raw_text: str,
                                     structured_data: Dict[str, Any],
                                     doc_type: DocumentType) -> List[ExtractedField]:
        """Extrait les champs selon le type de document"""
        
        if doc_type == DocumentType.AVIS_IMPOSITION:
            return self._extract_avis_imposition(raw_text, structured_data)
        
        elif doc_type == DocumentType.FEUILLE_SOINS:
            return self._extract_feuille_soins(raw_text, structured_data)
        
        elif doc_type == DocumentType.CARTE_GRISE:
            return self._extract_carte_grise(raw_text, structured_data)
        
        elif doc_type == DocumentType.BULLETIN_SALAIRE:
            return self._extract_bulletin_salaire(raw_text, structured_data)
        
        else:
            return self._extract_generic(raw_text, structured_data)
    
    def _extract_avis_imposition(self, text: str, 
                                 data: Dict[str, Any]) -> List[ExtractedField]:
        """Extraction spécifique avis d'imposition"""
        
        fields = []
        
        # Numéro fiscal
        numero_fiscal = self._extract_pattern(text, "numero_fiscal")
        if numero_fiscal:
            fields.append(ExtractedField(
                field_name="numero_fiscal",
                value=numero_fiscal[0],
                confidence=0.98
            ))
        
        # Année fiscale
        annee = self._extract_year(text)
        if annee:
            fields.append(ExtractedField(
                field_name="annee_fiscale",
                value=annee,
                confidence=0.99
            ))
        
        # Montants
        montants = data.get("montants", [])
        if len(montants) >= 3:
            fields.extend([
                ExtractedField("revenus_declares", montants[0], 0.95),
                ExtractedField("revenus_fonciers", montants[1], 0.92),
                ExtractedField("impot_du", montants[2], 0.97)
            ])
        
        # Identité
        personnes = data.get("personnes", [])
        if personnes:
            fields.append(ExtractedField(
                field_name="contribuable",
                value=personnes[0],
                confidence=0.96
            ))
        
        # Adresse
        adresses = data.get("adresses", [])
        if adresses:
            fields.append(ExtractedField(
                field_name="adresse_fiscale",
                value=adresses[0],
                confidence=0.94
            ))
        
        return fields
    
    def _extract_feuille_soins(self, text: str,
                               data: Dict[str, Any]) -> List[ExtractedField]:
        """Extraction feuille de soins"""
        
        fields = []
        
        # Numéro de sécurité sociale
        num_secu = self._extract_pattern(text, "numero_secu")
        if num_secu:
            fields.append(ExtractedField(
                "numero_securite_sociale",
                num_secu[0].replace(" ", ""),
                0.97
            ))
        
        # Date des soins
        dates = self._extract_pattern(text, "date")
        if dates:
            fields.append(ExtractedField(
                "date_soins",
                dates[0],
                0.95
            ))
        
        # Montants
        montants = data.get("montants", [])
        if montants:
            fields.append(ExtractedField(
                "montant_total",
                self._parse_amount(montants[0]),
                0.93
            ))
        
        return fields
    
    def _extract_carte_grise(self, text: str,
                            data: Dict[str, Any]) -> List[ExtractedField]:
        """Extraction carte grise"""
        
        fields = []
        
        # Immatriculation
        immat = self._extract_pattern(text, "immatriculation")
        if immat:
            fields.append(ExtractedField(
                "immatriculation",
                immat[0].replace(" ", "").replace("-", ""),
                0.99
            ))
        
        # Extraction marque/modèle (simplified)
        if "Marque" in text:
            marque_line = [line for line in text.split('\n') if "Marque" in line]
            if marque_line:
                fields.append(ExtractedField(
                    "marque",
                    marque_line[0].split(":")[-1].strip(),
                    0.90
                ))
        
        return fields
    
    def _extract_bulletin_salaire(self, text: str,
                                  data: Dict[str, Any]) -> List[ExtractedField]:
        """Extraction bulletin de salaire"""
        
        fields = []
        
        # Période
        dates = self._extract_pattern(text, "date")
        if dates:
            fields.append(ExtractedField("periode", dates[0], 0.94))
        
        # Salaire brut/net
        montants = data.get("montants", [])
        if len(montants) >= 2:
            fields.extend([
                ExtractedField("salaire_brut", montants[0], 0.96),
                ExtractedField("salaire_net", montants[-1], 0.97)
            ])
        
        # SIRET employeur
        siret = self._extract_pattern(text, "siret")
        if siret:
            fields.append(ExtractedField(
                "siret_employeur",
                siret[0].replace(" ", ""),
                0.95
            ))
        
        return fields
    
    def _extract_generic(self, text: str,
                        data: Dict[str, Any]) -> List[ExtractedField]:
        """Extraction générique pour types inconnus"""
        
        fields = []
        
        # Toutes les dates
        dates = self._extract_pattern(text, "date")
        for i, date in enumerate(dates[:3]):
            fields.append(ExtractedField(f"date_{i+1}", date, 0.85))
        
        # Tous les montants
        montants = data.get("montants", [])
        for i, montant in enumerate(montants[:5]):
            fields.append(ExtractedField(
                f"montant_{i+1}",
                self._parse_amount(montant),
                0.80
            ))
        
        return fields
    
    def _extract_pattern(self, text: str, pattern_name: str) -> List[str]:
        """Extrait toutes les occurrences d'un pattern"""
        pattern = self.PATTERNS.get(pattern_name)
        if not pattern:
            return []
        
        matches = re.findall(pattern, text)
        return matches
    
    def _extract_year(self, text: str) -> Optional[int]:
        """Extrait une année (2020-2030)"""
        years = re.findall(r'\b(202[0-9])\b', text)
        return int(years[0]) if years else None
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse un montant en float"""
        # Supprime espaces et remplace virgule par point
        cleaned = amount_str.replace(" ", "").replace(",", ".").replace("€", "")
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def _build_structured_data(self, fields: List[ExtractedField]) -> Dict[str, Any]:
        """Construit le JSON structuré final"""
        
        return {
            field.field_name: field.value
            for field in fields
        }
    
    def _validate(self, document: ExtractedDocument) -> List[str]:
        """Valide le document extrait"""
        
        errors = []
        
        # Vérification score de confiance global
        avg_confidence = sum(f.confidence for f in document.fields) / max(len(document.fields), 1)
        
        if avg_confidence < 0.80:
            errors.append(f"Confiance faible: {avg_confidence:.2f}")
        
        # Vérification présence champs obligatoires par type
        required_fields = self._get_required_fields(document.metadata.document_type)
        
        extracted_names = {f.field_name for f in document.fields}
        missing = set(required_fields) - extracted_names
        
        if missing:
            errors.append(f"Champs manquants: {', '.join(missing)}")
        
        return errors
    
    def _get_required_fields(self, doc_type: DocumentType) -> List[str]:
        """Retourne les champs obligatoires par type de document"""
        
        required = {
            DocumentType.AVIS_IMPOSITION: [
                "numero_fiscal", "annee_fiscale", "impot_du"
            ],
            DocumentType.FEUILLE_SOINS: [
                "numero_securite_sociale", "date_soins", "montant_total"
            ],
            DocumentType.CARTE_GRISE: [
                "immatriculation", "marque"
            ],
            DocumentType.BULLETIN_SALAIRE: [
                "periode", "salaire_net", "siret_employeur"
            ]
        }
        
        return required.get(doc_type, [])
    
    def _generate_document_id(self) -> str:
        """Génère un ID unique pour le document"""
        import uuid
        return f"DOC-{uuid.uuid4().hex[:12].upper()}"


# ============================================================================
# DATA MAPPER
# ============================================================================

class DataMapper:
    """
    Mappe les données extraites vers les formats attendus
    par les agents et les APIs externes
    """
    
    @staticmethod
    def to_json(extracted_doc: ExtractedDocument) -> str:
        """Convertit en JSON standardisé"""
        
        output = {
            "document_id": extracted_doc.metadata.document_id,
            "document_type": extracted_doc.metadata.document_type.value,
            "uploaded_at": extracted_doc.metadata.uploaded_at.isoformat(),
            "confidence_score": extracted_doc.metadata.confidence_score,
            "data": extracted_doc.structured_data,
            "validation": {
                "is_valid": len(extracted_doc.validation_errors) == 0,
                "errors": extracted_doc.validation_errors
            }
        }
        
        return json.dumps(output, indent=2, ensure_ascii=False)
    
    @staticmethod
    def to_agent_format(extracted_doc: ExtractedDocument) -> Dict[str, Any]:
        """Format optimisé pour les agents"""
        
        return {
            "id": extracted_doc.metadata.document_id,
            "type": extracted_doc.metadata.document_type.value,
            "fields": {
                field.field_name: {
                    "value": field.value,
                    "confidence": field.confidence
                }
                for field in extracted_doc.fields
            },
            "metadata": {
                "uploaded_at": extracted_doc.metadata.uploaded_at.isoformat(),
                "page_count": extracted_doc.metadata.page_count,
                "file_size": extracted_doc.metadata.file_size
            }
        }


# ============================================================================
# USAGE
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def demo():
        # Initialize OCR
        ocr = ClaudeVisionOCR()
        parser = DocumentParser(ocr)
        
        # Simulate document upload
        fake_image_data = b"fake_pdf_content"
        
        # Parse
        extracted = await parser.parse(
            fake_image_data,
            DocumentType.AVIS_IMPOSITION
        )
        
        # Output
        json_output = DataMapper.to_json(extracted)
        print(json_output)
        
        print(f"\nExtracted {len(extracted.fields)} fields")
        print(f"Confidence: {extracted.metadata.confidence_score:.2%}")
        print(f"Errors: {len(extracted.validation_errors)}")
    
    asyncio.run(demo())
