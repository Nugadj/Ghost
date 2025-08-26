"""
Ghost Protocol Cryptography Utilities
"""

import os
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from nacl.secret import SecretBox
from nacl.utils import random
import base64


class CertificateManager:
    """Manages SSL certificates and cryptographic operations"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("ghost_protocol.crypto")
        self.cert_dir = "certs"
        self.private_key = None
        self.certificate = None
        self.fingerprint = None
        
    async def initialize(self) -> bool:
        """Initialize certificate manager"""
        try:
            # Create certs directory
            os.makedirs(self.cert_dir, exist_ok=True)
            
            # Load or generate certificates
            if not await self._load_existing_certificates():
                await self._generate_certificates()
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize certificate manager: {e}")
            return False
            
    async def _load_existing_certificates(self) -> bool:
        """Load existing certificates"""
        cert_file = os.path.join(self.cert_dir, "server.crt")
        key_file = os.path.join(self.cert_dir, "server.key")
        
        if not (os.path.exists(cert_file) and os.path.exists(key_file)):
            return False
            
        try:
            # Load certificate
            with open(cert_file, "rb") as f:
                cert_data = f.read()
                self.certificate = x509.load_pem_x509_certificate(cert_data)
                
            # Load private key
            with open(key_file, "rb") as f:
                key_data = f.read()
                self.private_key = serialization.load_pem_private_key(
                    key_data, password=None
                )
                
            # Generate fingerprint
            self.fingerprint = hashlib.sha256(cert_data).hexdigest()
            
            self.logger.info("Loaded existing certificates")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading certificates: {e}")
            return False
            
    async def _generate_certificates(self):
        """Generate new SSL certificates"""
        try:
            # Generate private key
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Generate certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Ghost Protocol"),
                x509.NameAttribute(NameOID.COMMON_NAME, "ghostprotocol.local"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                self.private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=3650)  # 10 years
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.DNSName("ghostprotocol.local"),
                    x509.IPAddress("127.0.0.1"),
                ]),
                critical=False,
            ).sign(self.private_key, hashes.SHA256())
            
            self.certificate = cert
            
            # Save certificate and key
            cert_file = os.path.join(self.cert_dir, "server.crt")
            key_file = os.path.join(self.cert_dir, "server.key")
            
            with open(cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
                
            with open(key_file, "wb") as f:
                f.write(self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
                
            # Generate fingerprint
            cert_data = cert.public_bytes(serialization.Encoding.PEM)
            self.fingerprint = hashlib.sha256(cert_data).hexdigest()
            
            self.logger.info("Generated new SSL certificates")
            
        except Exception as e:
            self.logger.error(f"Error generating certificates: {e}")
            raise
            
    def get_fingerprint(self) -> Optional[str]:
        """Get certificate fingerprint"""
        return self.fingerprint
        
    def get_cert_files(self) -> Tuple[str, str]:
        """Get certificate file paths"""
        cert_file = os.path.join(self.cert_dir, "server.crt")
        key_file = os.path.join(self.cert_dir, "server.key")
        return cert_file, key_file


class EncryptionManager:
    """Manages data encryption and decryption"""
    
    def __init__(self, key: Optional[bytes] = None):
        self.logger = logging.getLogger("ghost_protocol.encryption")
        if key:
            self.secret_box = SecretBox(key)
        else:
            self.secret_box = SecretBox(random(SecretBox.KEY_SIZE))
            
    def encrypt(self, data: bytes) -> str:
        """Encrypt data and return base64 encoded result"""
        try:
            encrypted = self.secret_box.encrypt(data)
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Encryption error: {e}")
            raise
            
    def decrypt(self, encrypted_data: str) -> bytes:
        """Decrypt base64 encoded data"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            return self.secret_box.decrypt(encrypted_bytes)
        except Exception as e:
            self.logger.error(f"Decryption error: {e}")
            raise
            
    def encrypt_string(self, text: str) -> str:
        """Encrypt string data"""
        return self.encrypt(text.encode('utf-8'))
        
    def decrypt_string(self, encrypted_data: str) -> str:
        """Decrypt to string"""
        return self.decrypt(encrypted_data).decode('utf-8')
