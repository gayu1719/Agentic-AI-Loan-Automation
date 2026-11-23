"""
Enterprise Security Framework for Agentic LOS
Provides advanced security, compliance, and audit capabilities for banking systems.
"""

import os
import jwt
import bcrypt
import secrets
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import hashlib
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class UserRole(Enum):
    """User roles with hierarchical permissions."""
    LOAN_OFFICER = "loan_officer"
    SENIOR_UNDERWRITER = "senior_underwriter" 
    RISK_MANAGER = "risk_manager"
    COMPLIANCE_OFFICER = "compliance_officer"
    PORTFOLIO_MANAGER = "portfolio_manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

@dataclass
class SecurityContext:
    """Security context for user sessions."""
    user_id: str
    username: str
    role: UserRole
    permissions: List[str]
    session_id: str
    ip_address: str
    device_fingerprint: str
    expires_at: datetime
    mfa_verified: bool = False

class EnterpriseSecurityFramework:
    """Comprehensive security framework for banking applications."""
    
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
        self.encryption_key = self._derive_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.session_timeout = timedelta(hours=8)
        self.failed_attempts = {}  # Track failed login attempts
        self.active_sessions = {}  # Track active user sessions
        
    def _derive_encryption_key(self) -> bytes:
        """Derive encryption key from password."""
        password = os.getenv("ENCRYPTION_PASSWORD", "default_password").encode()
        salt = os.getenv("ENCRYPTION_SALT", "default_salt").encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def authenticate_user(self, username: str, password: str, ip_address: str) -> Optional[SecurityContext]:
        """Authenticate user with multi-factor considerations."""
        
        # Check for account lockout
        if self._is_account_locked(username, ip_address):
            raise SecurityException("Account temporarily locked due to failed attempts")
        
        # Validate credentials (in production, query from secure database)
        if not self._validate_credentials(username, password):
            self._record_failed_attempt(username, ip_address)
            return None
            
        # Get user role and permissions
        user_role, permissions = self._get_user_permissions(username)
        
        # Create security context
        context = SecurityContext(
            user_id=self._get_user_id(username),
            username=username,
            role=user_role,
            permissions=permissions,
            session_id=secrets.token_urlsafe(32),
            ip_address=ip_address,
            device_fingerprint=self._generate_device_fingerprint(ip_address),
            expires_at=datetime.now() + self.session_timeout
        )
        
        # Store active session
        self.active_sessions[context.session_id] = context
        
        return context
    
    def generate_jwt_token(self, context: SecurityContext) -> str:
        """Generate JWT token for authenticated user."""
        payload = {
            "user_id": context.user_id,
            "username": context.username,
            "role": context.role.value,
            "session_id": context.session_id,
            "exp": context.expires_at,
            "iat": datetime.now(),
            "permissions": context.permissions
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def validate_jwt_token(self, token: str) -> Optional[SecurityContext]:
        """Validate JWT token and return security context."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            session_id = payload.get("session_id")
            
            # Check if session is still active
            if session_id not in self.active_sessions:
                return None
                
            context = self.active_sessions[session_id]
            
            # Check expiration
            if datetime.now() > context.expires_at:
                del self.active_sessions[session_id]
                return None
                
            return context
            
        except jwt.InvalidTokenError:
            return None
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data using Fernet symmetric encryption."""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    def check_permission(self, context: SecurityContext, required_permission: str) -> bool:
        """Check if user has required permission."""
        return required_permission in context.permissions
    
    def _is_account_locked(self, username: str, ip_address: str) -> bool:
        """Check if account is locked due to failed attempts."""
        key = f"{username}:{ip_address}"
        if key in self.failed_attempts:
            attempts, last_attempt = self.failed_attempts[key]
            if attempts >= 5 and datetime.now() - last_attempt < timedelta(minutes=30):
                return True
        return False
    
    def _record_failed_attempt(self, username: str, ip_address: str):
        """Record failed login attempt."""
        key = f"{username}:{ip_address}"
        if key in self.failed_attempts:
            attempts, _ = self.failed_attempts[key]
            self.failed_attempts[key] = (attempts + 1, datetime.now())
        else:
            self.failed_attempts[key] = (1, datetime.now())
    
    def _validate_credentials(self, username: str, password: str) -> bool:
        """Validate user credentials (mock implementation)."""
        # In production, query secure database with hashed passwords
        mock_users = {
            "loan_officer": "$2b$12$example_hashed_password",
            "underwriter": "$2b$12$example_hashed_password2", 
            "risk_manager": "$2b$12$example_hashed_password3"
        }
        
        if username not in mock_users:
            return False
            
        # In production, use bcrypt.checkpw(password.encode(), hashed_password)
        return True  # Simplified for demo
    
    def _get_user_permissions(self, username: str) -> tuple[UserRole, List[str]]:
        """Get user role and permissions."""
        
        # Role-based permissions mapping
        role_permissions = {
            UserRole.LOAN_OFFICER: [
                "submit_application", "view_application", "upload_documents"
            ],
            UserRole.SENIOR_UNDERWRITER: [
                "submit_application", "view_application", "upload_documents",
                "review_application", "request_additional_info", "preliminary_approval"
            ],
            UserRole.RISK_MANAGER: [
                "view_application", "review_application", "view_portfolio_risk",
                "set_risk_limits", "approve_high_risk", "generate_risk_reports"
            ],
            UserRole.COMPLIANCE_OFFICER: [
                "view_application", "compliance_review", "audit_decisions",
                "generate_compliance_reports", "view_audit_logs"
            ],
            UserRole.PORTFOLIO_MANAGER: [
                "view_portfolio", "portfolio_analysis", "set_strategies",
                "approve_portfolio_limits", "view_performance_metrics"
            ],
            UserRole.ADMIN: [
                "user_management", "system_configuration", "view_system_metrics",
                "manage_integrations", "backup_restore"
            ]
        }
        
        # Mock user-role mapping (in production, query from database)
        user_roles = {
            "loan_officer": UserRole.LOAN_OFFICER,
            "underwriter": UserRole.SENIOR_UNDERWRITER,
            "risk_manager": UserRole.RISK_MANAGER
        }
        
        role = user_roles.get(username, UserRole.LOAN_OFFICER)
        permissions = role_permissions.get(role, [])
        
        return role, permissions
    
    def _get_user_id(self, username: str) -> str:
        """Get user ID for username."""
        return hashlib.sha256(username.encode()).hexdigest()[:12]
    
    def _generate_device_fingerprint(self, ip_address: str) -> str:
        """Generate device fingerprint for session tracking."""
        return hashlib.sha256(f"{ip_address}:{datetime.now().date()}".encode()).hexdigest()[:16]


class ComplianceFramework:
    """Banking compliance and regulatory framework."""
    
    def __init__(self):
        self.audit_logger = logging.getLogger("compliance_audit")
        self.regulations = self._load_regulations()
        
    def _load_regulations(self) -> Dict[str, Any]:
        """Load regulatory requirements."""
        return {
            "basel_iii": {
                "capital_requirements": {"tier1": 0.06, "total": 0.08},
                "liquidity_coverage": 1.0,
                "leverage_ratio": 0.03
            },
            "sox_compliance": {
                "audit_trail_retention": 2555,  # days (7 years)
                "decision_documentation": True,
                "segregation_of_duties": True
            },
            "gdpr": {
                "data_retention": 2555,  # days
                "consent_required": True,
                "right_to_erasure": True,
                "data_portability": True
            },
            "pci_dss": {
                "encryption_at_rest": True,
                "encryption_in_transit": True,
                "access_logging": True,
                "regular_testing": True
            }
        }
    
    def validate_loan_compliance(self, loan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate loan against regulatory requirements."""
        compliance_result = {
            "compliant": True,
            "violations": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Basel III Capital Requirements
        if "capital_ratio" in loan_data:
            tier1_ratio = loan_data.get("tier1_capital_ratio", 0)
            if tier1_ratio < self.regulations["basel_iii"]["capital_requirements"]["tier1"]:
                compliance_result["violations"].append(
                    f"Tier 1 capital ratio {tier1_ratio:.2%} below required {self.regulations['basel_iii']['capital_requirements']['tier1']:.2%}"
                )
                compliance_result["compliant"] = False
        
        # GDPR Data Requirements 
        if not loan_data.get("customer_consent", False):
            compliance_result["violations"].append("Customer consent not documented (GDPR violation)")
            compliance_result["compliant"] = False
        
        # SOX Documentation Requirements
        if not loan_data.get("decision_documentation", False):
            compliance_result["warnings"].append("Insufficient decision documentation for SOX compliance")
        
        return compliance_result
    
    def log_compliance_event(self, event_type: str, details: Dict[str, Any]):
        """Log compliance-related events."""
        self.audit_logger.info(
            f"COMPLIANCE_EVENT",
            extra={
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "details": details
            }
        )


class AuditTrailManager:
    """Comprehensive audit trail management."""
    
    def __init__(self):
        self.audit_log = []
        
    def log_decision(self, decision_data: Dict[str, Any], user_context: SecurityContext):
        """Log loan decision for audit purposes."""
        audit_entry = {
            "id": secrets.token_urlsafe(16),
            "timestamp": datetime.now().isoformat(),
            "event_type": "loan_decision",
            "user_id": user_context.user_id,
            "username": user_context.username,
            "user_role": user_context.role.value,
            "session_id": user_context.session_id,
            "ip_address": user_context.ip_address,
            "decision_data": {
                "application_id": decision_data.get("application_id"),
                "decision": decision_data.get("decision"),
                "confidence_score": decision_data.get("confidence_score"),
                "risk_score": decision_data.get("risk_score"),
                "loan_amount": decision_data.get("loan_amount"),
                "industry": decision_data.get("industry")
            },
            "ai_model_versions": decision_data.get("model_versions", {}),
            "compliance_flags": decision_data.get("compliance_flags", [])
        }
        
        self.audit_log.append(audit_entry)
        
    def get_audit_trail(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieve audit trail with optional filters."""
        if not filters:
            return self.audit_log
            
        filtered_log = []
        for entry in self.audit_log:
            match = True
            for key, value in filters.items():
                if key not in entry or entry[key] != value:
                    match = False
                    break
            if match:
                filtered_log.append(entry)
                
        return filtered_log


class SecurityException(Exception):
    """Custom exception for security-related errors."""
    pass


# Usage example
if __name__ == "__main__":
    # Initialize security framework
    security = EnterpriseSecurityFramework()
    compliance = ComplianceFramework()
    audit = AuditTrailManager()
    
    # Example authentication flow
    try:
        context = security.authenticate_user("loan_officer", "password", "192.168.1.100")
        if context:
            token = security.generate_jwt_token(context)
            print(f"Authentication successful, token: {token[:50]}...")
            
            # Example compliance check
            loan_data = {
                "tier1_capital_ratio": 0.08,
                "customer_consent": True,
                "decision_documentation": True
            }
            
            compliance_result = compliance.validate_loan_compliance(loan_data)
            print(f"Compliance check: {compliance_result}")
            
    except SecurityException as e:
        print(f"Security error: {e}") 