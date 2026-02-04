"""
GAIU 4 - Module de Sécurité
Data Vault + AES-256 Encryption + FranceConnect+
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets
import base64
import json
from abc import ABC, abstractmethod


# ============================================================================
# CRYPTOGRAPHY (Production: use cryptography library)
# ============================================================================

class EncryptionAlgorithm(Enum):
    """Algorithmes de chiffrement supportés"""
    AES_256_GCM = "aes-256-gcm"
    AES_256_CBC = "aes-256-cbc"
    CHACHA20_POLY1305 = "chacha20-poly1305"


@dataclass
class EncryptionKey:
    """Clé de chiffrement avec métadonnées"""
    key_id: str
    key_material: bytes
    algorithm: EncryptionAlgorithm
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    version: int = 1
    

@dataclass
class EncryptedData:
    """Données chiffrées avec métadonnées"""
    ciphertext: bytes
    algorithm: EncryptionAlgorithm
    key_id: str
    iv: bytes  # Initialization Vector
    auth_tag: Optional[bytes] = None  # Pour GCM
    metadata: Dict[str, Any] = field(default_factory=dict)


class AESEncryption:
    """
    Chiffrement AES-256-GCM
    Production: utiliser cryptography.hazmat
    """
    
    @staticmethod
    def generate_key() -> bytes:
        """Génère une clé AES-256 (32 bytes)"""
        return secrets.token_bytes(32)
    
    @staticmethod
    def generate_iv() -> bytes:
        """Génère un IV aléatoire (12 bytes pour GCM)"""
        return secrets.token_bytes(12)
    
    @staticmethod
    def encrypt(plaintext: bytes, key: bytes, 
                associated_data: Optional[bytes] = None) -> EncryptedData:
        """
        Chiffre avec AES-256-GCM
        
        En production, utiliser:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        """
        
        # Simulation - PROD: AESGCM(key).encrypt(iv, plaintext, associated_data)
        iv = AESEncryption.generate_iv()
        
        # Pseudo-encryption pour la démo
        # En réalité: utiliser AESGCM
        ciphertext = base64.b64encode(plaintext)
        auth_tag = hashlib.sha256(plaintext + key + iv).digest()[:16]
        
        return EncryptedData(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_id="master_key_001",
            iv=iv,
            auth_tag=auth_tag,
            metadata={
                "encrypted_at": datetime.utcnow().isoformat(),
                "size": len(plaintext)
            }
        )
    
    @staticmethod
    def decrypt(encrypted: EncryptedData, key: bytes,
                associated_data: Optional[bytes] = None) -> bytes:
        """
        Déchiffre avec AES-256-GCM
        
        En production:
        AESGCM(key).decrypt(iv, ciphertext, associated_data)
        """
        
        # Simulation - PROD: utiliser AESGCM
        plaintext = base64.b64decode(encrypted.ciphertext)
        
        # Vérification de l'auth_tag (AEAD)
        # En prod, AESGCM le fait automatiquement
        
        return plaintext


# ============================================================================
# DATA VAULT
# ============================================================================

class DataClassification(Enum):
    """Niveaux de classification des données"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


@dataclass
class VaultRecord:
    """Enregistrement dans le coffre-fort"""
    record_id: str
    user_id: str
    data_type: str
    classification: DataClassification
    encrypted_data: EncryptedData
    created_at: datetime = field(default_factory=datetime.utcnow)
    accessed_at: Optional[datetime] = None
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataVault:
    """
    Coffre-fort pour données sensibles
    Architecture: Encryption at rest + access control
    """
    
    def __init__(self):
        self.master_key = AESEncryption.generate_key()
        self.records: Dict[str, VaultRecord] = {}
        self.key_rotation_days = 90
        
    def store(self, user_id: str, data: Dict[str, Any],
             data_type: str,
             classification: DataClassification = DataClassification.CONFIDENTIAL) -> str:
        """
        Stocke des données sensibles chiffrées
        
        Args:
            user_id: ID de l'utilisateur propriétaire
            data: Données à chiffrer
            data_type: Type de données (fiscal, health, etc.)
            classification: Niveau de sensibilité
        
        Returns:
            record_id: Identifiant du record
        """
        
        # Sérialisation
        plaintext = json.dumps(data, ensure_ascii=False).encode('utf-8')
        
        # Chiffrement avec métadonnées associées
        associated_data = f"{user_id}:{data_type}".encode('utf-8')
        encrypted = AESEncryption.encrypt(
            plaintext,
            self.master_key,
            associated_data
        )
        
        # Création du record
        record_id = self._generate_record_id()
        
        vault_record = VaultRecord(
            record_id=record_id,
            user_id=user_id,
            data_type=data_type,
            classification=classification,
            encrypted_data=encrypted,
            metadata={
                "size_bytes": len(plaintext),
                "fields": list(data.keys())
            }
        )
        
        self.records[record_id] = vault_record
        
        return record_id
    
    def retrieve(self, record_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère et déchiffre des données
        
        Args:
            record_id: ID du record
            user_id: ID utilisateur (pour contrôle d'accès)
        
        Returns:
            Données déchiffrées ou None si accès refusé
        """
        
        record = self.records.get(record_id)
        
        if not record:
            return None
        
        # Contrôle d'accès
        if record.user_id != user_id:
            raise PermissionError(f"Accès refusé au record {record_id}")
        
        # Déchiffrement
        associated_data = f"{user_id}:{record.data_type}".encode('utf-8')
        
        plaintext = AESEncryption.decrypt(
            record.encrypted_data,
            self.master_key,
            associated_data
        )
        
        # Audit
        record.accessed_at = datetime.utcnow()
        record.access_count += 1
        
        # Désérialisation
        return json.loads(plaintext.decode('utf-8'))
    
    def delete(self, record_id: str, user_id: str) -> bool:
        """Supprime un record (RGPD: droit à l'effacement)"""
        
        record = self.records.get(record_id)
        
        if not record:
            return False
        
        if record.user_id != user_id:
            raise PermissionError("Accès refusé")
        
        # Suppression sécurisée
        del self.records[record_id]
        
        return True
    
    def rotate_keys(self):
        """
        Rotation des clés de chiffrement
        Recommandé tous les 90 jours
        """
        
        new_master_key = AESEncryption.generate_key()
        
        # Re-chiffrement de tous les records
        for record in self.records.values():
            
            # Déchiffrement avec ancienne clé
            associated_data = f"{record.user_id}:{record.data_type}".encode('utf-8')
            plaintext = AESEncryption.decrypt(
                record.encrypted_data,
                self.master_key,
                associated_data
            )
            
            # Re-chiffrement avec nouvelle clé
            new_encrypted = AESEncryption.encrypt(
                plaintext,
                new_master_key,
                associated_data
            )
            
            record.encrypted_data = new_encrypted
        
        # Mise à jour de la master key
        self.master_key = new_master_key
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export complet des données utilisateur (RGPD)
        """
        
        user_records = [
            record for record in self.records.values()
            if record.user_id == user_id
        ]
        
        export = {
            "user_id": user_id,
            "export_date": datetime.utcnow().isoformat(),
            "records": []
        }
        
        for record in user_records:
            data = self.retrieve(record.record_id, user_id)
            
            export["records"].append({
                "record_id": record.record_id,
                "data_type": record.data_type,
                "classification": record.classification.value,
                "created_at": record.created_at.isoformat(),
                "data": data
            })
        
        return export
    
    def _generate_record_id(self) -> str:
        """Génère un ID unique pour un record"""
        return f"VLT-{secrets.token_hex(16).upper()}"


# ============================================================================
# FRANCECONNECT+ AUTHENTICATION
# ============================================================================

class AuthLevel(Enum):
    """Niveaux d'authentification FranceConnect"""
    BASIC = "basic"              # FranceConnect standard
    SUBSTANTIAL = "substantial"   # FranceConnect+
    HIGH = "high"                # FranceConnect+ niveau élevé


@dataclass
class FranceConnectProfile:
    """Profil utilisateur FranceConnect"""
    sub: str  # Subject identifier (unique)
    given_name: str
    family_name: str
    birthdate: str
    gender: Optional[str] = None
    birthplace: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    preferred_username: Optional[str] = None
    

@dataclass
class AuthSession:
    """Session d'authentification"""
    session_id: str
    user_id: str
    fc_profile: FranceConnectProfile
    auth_level: AuthLevel
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=2))
    tokens: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FranceConnectAuthenticator:
    """
    Gestionnaire d'authentification FranceConnect+
    
    Flux OAuth 2.0 / OpenID Connect
    """
    
    # Configuration FranceConnect
    FC_AUTHORIZE_URL = "https://app.franceconnect.gouv.fr/api/v1/authorize"
    FC_TOKEN_URL = "https://app.franceconnect.gouv.fr/api/v1/token"
    FC_USERINFO_URL = "https://app.franceconnect.gouv.fr/api/v1/userinfo"
    FC_LOGOUT_URL = "https://app.franceconnect.gouv.fr/api/v1/logout"
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.sessions: Dict[str, AuthSession] = {}
    
    def generate_authorization_url(self, acr: AuthLevel = AuthLevel.SUBSTANTIAL) -> Tuple[str, str]:
        """
        Génère l'URL d'autorisation FranceConnect
        
        Returns:
            (url, state): URL de redirection et paramètre state
        """
        
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid profile email phone",
            "state": state,
            "nonce": nonce,
            "acr_values": self._get_acr_value(acr)
        }
        
        # En production: utiliser urllib.parse.urlencode
        url = f"{self.FC_AUTHORIZE_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        
        return url, state
    
    async def handle_callback(self, code: str, state: str) -> AuthSession:
        """
        Traite le callback après authentification
        
        Args:
            code: Code d'autorisation
            state: Paramètre state pour validation
        
        Returns:
            Session d'authentification créée
        """
        
        # 1. Échange du code contre un access_token
        token_response = await self._exchange_code_for_token(code)
        
        access_token = token_response.get("access_token")
        id_token = token_response.get("id_token")
        
        # 2. Récupération du profil utilisateur
        fc_profile = await self._get_user_info(access_token)
        
        # 3. Vérification du niveau d'authentification
        auth_level = self._verify_auth_level(id_token)
        
        # 4. Création de la session
        session_id = self._generate_session_id()
        
        session = AuthSession(
            session_id=session_id,
            user_id=fc_profile.sub,
            fc_profile=fc_profile,
            auth_level=auth_level,
            tokens={
                "access_token": access_token,
                "id_token": id_token
            },
            metadata={
                "ip_address": "0.0.0.0",  # À récupérer de la requête
                "user_agent": "Mozilla/5.0"
            }
        )
        
        self.sessions[session_id] = session
        
        return session
    
    async def _exchange_code_for_token(self, code: str) -> Dict[str, str]:
        """Échange le code d'autorisation contre des tokens"""
        
        # Simulation - En production: requête POST
        # import httpx
        # response = await httpx.post(self.FC_TOKEN_URL, data=...)
        
        return {
            "access_token": f"fc_access_{secrets.token_urlsafe(32)}",
            "id_token": f"fc_id_{secrets.token_urlsafe(32)}",
            "token_type": "Bearer",
            "expires_in": 3600
        }
    
    async def _get_user_info(self, access_token: str) -> FranceConnectProfile:
        """Récupère les informations utilisateur"""
        
        # Simulation - En production: requête GET avec Bearer token
        # headers = {"Authorization": f"Bearer {access_token}"}
        # response = await httpx.get(self.FC_USERINFO_URL, headers=headers)
        
        return FranceConnectProfile(
            sub="fc_user_123456789",
            given_name="Jean",
            family_name="DUPONT",
            birthdate="1985-05-15",
            gender="male",
            email="jean.dupont@example.fr"
        )
    
    def _verify_auth_level(self, id_token: str) -> AuthLevel:
        """Vérifie le niveau d'authentification atteint"""
        
        # En production: décoder le JWT et vérifier le claim 'acr'
        # import jwt
        # decoded = jwt.decode(id_token, verify=False)
        # acr = decoded.get('acr')
        
        return AuthLevel.SUBSTANTIAL
    
    def validate_session(self, session_id: str) -> bool:
        """Valide qu'une session est active et non expirée"""
        
        session = self.sessions.get(session_id)
        
        if not session:
            return False
        
        if datetime.utcnow() > session.expires_at:
            del self.sessions[session_id]
            return False
        
        return True
    
    def get_session(self, session_id: str) -> Optional[AuthSession]:
        """Récupère une session active"""
        
        if not self.validate_session(session_id):
            return None
        
        return self.sessions.get(session_id)
    
    async def logout(self, session_id: str):
        """Déconnexion et révocation des tokens"""
        
        session = self.sessions.get(session_id)
        
        if session:
            # Révocation des tokens FranceConnect
            # En production: appel à l'endpoint de logout FC
            
            del self.sessions[session_id]
    
    def _get_acr_value(self, auth_level: AuthLevel) -> str:
        """Convertit le niveau d'auth en valeur ACR"""
        
        acr_map = {
            AuthLevel.BASIC: "eidas1",
            AuthLevel.SUBSTANTIAL: "eidas2",
            AuthLevel.HIGH: "eidas3"
        }
        
        return acr_map.get(auth_level, "eidas1")
    
    def _generate_session_id(self) -> str:
        """Génère un ID de session sécurisé"""
        return f"SESS-{secrets.token_urlsafe(32)}"


# ============================================================================
# USAGE
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    # ---- DATA VAULT ----
    vault = DataVault()
    
    # Stockage de données sensibles
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
    
    print(f"Record stocké: {record_id}")
    
    # Récupération
    retrieved = vault.retrieve(record_id, "user_123")
    print(f"Récupéré: {retrieved}")
    
    # ---- FRANCECONNECT ----
    fc_auth = FranceConnectAuthenticator(
        client_id="gaiu4_client",
        client_secret="secret_key",
        redirect_uri="https://gaiu4.app/auth/callback"
    )
    
    # Génération URL d'authentification
    auth_url, state = fc_auth.generate_authorization_url(
        acr=AuthLevel.SUBSTANTIAL
    )
    
    print(f"\nURL FranceConnect: {auth_url[:80]}...")
    
    # Simulation callback
    async def demo_auth():
        session = await fc_auth.handle_callback(
            code="authorization_code_123",
            state=state
        )
        
        print(f"\nSession créée: {session.session_id}")
        print(f"Utilisateur: {session.fc_profile.given_name} {session.fc_profile.family_name}")
        print(f"Niveau auth: {session.auth_level.value}")
    
    asyncio.run(demo_auth())
