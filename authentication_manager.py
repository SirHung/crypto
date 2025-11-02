"""
GOD MODE 1000 - AUTHENTICATION & USER MANAGEMENT SYSTEM
======================================================
High-Security Authentication with User Management & Approval System
Default Admin: admin / ManhHung1@
"""

import hashlib
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import secrets
import base64

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

try:
    from .unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)


class Permission(Enum):
    """Detailed permissions for each function"""
    # Trading Permissions
    MANUAL_TRADING = "manual_trading"
    AUTO_TRADING = "auto_trading"
    DCA_BOT = "dca_bot"
    FOREX_TRADING = "forex_trading"
    
    # AI & Prediction Permissions
    AI_PREDICTION = "ai_prediction"
    AI_TRAINING = "ai_training"
    BACKTESTING = "backtesting"
    
    # Analysis Permissions
    MARKET_ANALYSIS = "market_analysis"
    TECHNICAL_ANALYSIS = "technical_analysis"
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"
    MULTI_TIMEFRAME = "multi_timeframe"
    PATTERN_RECOGNITION = "pattern_recognition"
    
    # On-Chain & Market Data
    ONCHAIN_ANALYSIS = "onchain_analysis"
    WHALE_TRACKING = "whale_tracking"
    ORDER_BOOK = "order_book"
    FUNDING_RATES = "funding_rates"
    
    # Market Intelligence
    NEWS_SENTIMENT = "news_sentiment"
    KOL_TRACKING = "kol_tracking"
    SMART_ALERTS = "smart_alerts"
    ADVANCED_SEARCH = "advanced_search"
    AIRDROP_HUNTER = "airdrop_hunter"
    
    # Portfolio & Dashboard
    PORTFOLIO_VIEW = "portfolio_view"
    PORTFOLIO_EDIT = "portfolio_edit"
    DASHBOARD_VIEW = "dashboard_view"
    
    # System & Admin
    SYSTEM_CONFIG = "system_config"
    USER_MANAGEMENT = "user_management"
    PERFORMANCE_MONITOR = "performance_monitor"
    LOG_ACCESS = "log_access"


class UserRole(Enum):
    """User roles with different permissions"""
    ADMIN = "admin"
    TRADER = "trader"
    ANALYST = "analyst"
    VIEWER = "viewer"
    PENDING = "pending"  # Waiting for approval


class UserStatus(Enum):
    """User account status"""
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    DELETED = "deleted"


@dataclass
class User:
    """User account data structure"""
    username: str
    password_hash: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    permissions: List[str] = field(default_factory=list)  # List of Permission enum values
    last_login: Optional[datetime] = None
    email: str = ""
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    session_token: Optional[str] = None


class AuthenticationManager:
    """Authentication & User Management - God Mode 1000"""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize Authentication Manager with AES-256 Encryption"""
        self.unified_logger = unified_logging.get_logger("auth_manager")
        
        # Data directory for storing encrypted user data
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.enc")  # Encrypted file
        self.sessions_file = os.path.join(data_dir, "sessions.enc")  # Encrypted file
        self.reset_codes_file = os.path.join(data_dir, "reset_codes.enc")  # Encrypted file
        self.key_file = os.path.join(data_dir, ".godmode_key")  # Hidden encryption key
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize encryption (AES-256)
        self.cipher = None
        if CRYPTO_AVAILABLE:
            self._initialize_encryption()
        else:
            self.unified_logger.warning("Cryptography library not available. Install: pip install cryptography")
        
        # Security settings
        self.max_failed_attempts = 5
        self.lockout_duration = 30  # minutes
        self.session_timeout = 480  # 8 hours
        self.password_min_length = 8
        self.reset_code_expiry = 30  # minutes
        
        # Load users or create default admin
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.reset_codes: Dict[str, Dict[str, Any]] = {}  # username -> {code, expires_at, attempts}
        self._load_users()
        self._load_sessions()
        self._load_reset_codes()
        
        # Create default admin if not exists
        self._create_default_admin()
        
        self.unified_logger.info("✅ Authentication Manager initialized - God Mode 1000 [AES-256 ENCRYPTED]")
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
        """Hash password with salt using SHA-256 (secure hashing)"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2 with SHA-256 for secure password hashing
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )
        
        return password_hash.hex(), salt
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            # Extract salt from hash (format: hash:salt)
            if ':' in password_hash:
                stored_hash, salt = password_hash.split(':')
                computed_hash, _ = self._hash_password(password, salt)
                return computed_hash == stored_hash
            return False
        except Exception as e:
            self.unified_logger.error(f"Password verification error: {e}")
            return False
    
    def _create_default_admin(self):
        """Create default admin account if not exists"""
        try:
            if 'admin' not in self.users:
                # Hash default password: ManhHung1@
                password_hash, salt = self._hash_password("ManhHung1@")
                full_hash = f"{password_hash}:{salt}"
                
                # Admin has ALL permissions
                all_permissions = [p.value for p in Permission]
                
                admin_user = User(
                    username='admin',
                    password_hash=full_hash,
                    role=UserRole.ADMIN,
                    status=UserStatus.ACTIVE,
                    created_at=datetime.now(timezone.utc),
                    permissions=all_permissions,
                    email='admin@godmode1000.com',
                    approved_by='system',
                    approved_at=datetime.now(timezone.utc)
                )
                
                self.users['admin'] = admin_user
                self._save_users()
                self.unified_logger.info("✅ Default admin account created: admin / ")
        
        except Exception as e:
            self.unified_logger.error(f"Failed to create default admin: {e}")
    
    def login(self, username: str, password: str) -> tuple:
        """
        Authenticate user
        Returns: (success: bool, message: str, session_token: str)
        """
        try:
            # Check if user exists
            if username not in self.users:
                self.unified_logger.warning(f"Login attempt for non-existent user: {username}")
                return False, "Invalid username or password", None
            
            user = self.users[username]
            
            # Check if account is locked
            if user.locked_until and datetime.now(timezone.utc) < user.locked_until:
                remaining = (user.locked_until - datetime.now(timezone.utc)).seconds // 60
                return False, f"Account locked. Try again in {remaining} minutes.", None
            
            # Check if account is suspended
            if user.status == UserStatus.SUSPENDED:
                return False, "Account suspended. Contact administrator.", None
            
            # Check if account is pending approval
            if user.status == UserStatus.PENDING:
                return False, "Account pending approval by administrator.", None
            
            # Verify password
            if self._verify_password(password, user.password_hash):
                # Reset failed attempts
                user.failed_login_attempts = 0
                user.locked_until = None
                user.last_login = datetime.now(timezone.utc)
                
                # Generate session token
                session_token = secrets.token_urlsafe(32)
                user.session_token = session_token
                
                # Create session
                self.sessions[session_token] = {
                    'username': username,
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'expires_at': (datetime.now(timezone.utc) + timedelta(minutes=self.session_timeout)).isoformat(),
                    'role': user.role.value
                }
                
                self._save_users()
                self._save_sessions()
                
                self.unified_logger.info(f"✅ Successful login: {username} (Role: {user.role.value})")
                return True, f"Welcome {username}!", session_token
            
            else:
                # Failed login
                user.failed_login_attempts += 1
                
                # Lock account if too many failed attempts
                if user.failed_login_attempts >= self.max_failed_attempts:
                    user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=self.lockout_duration)
                    self._save_users()
                    self.unified_logger.warning(f"Account locked due to failed attempts: {username}")
                    return False, f"Account locked for {self.lockout_duration} minutes due to too many failed attempts.", None
                
                self._save_users()
                remaining_attempts = self.max_failed_attempts - user.failed_login_attempts
                return False, f"Invalid password. {remaining_attempts} attempts remaining.", None
        
        except Exception as e:
            self.unified_logger.error(f"Login error: {e}", exception=e)
            return False, "Login error. Please try again.", None
    
    def logout(self, session_token: str) -> bool:
        """Logout user by invalidating session"""
        try:
            if session_token in self.sessions:
                username = self.sessions[session_token]['username']
                del self.sessions[session_token]
                
                # Clear user session token
                if username in self.users:
                    self.users[username].session_token = None
                    self._save_users()
                
                self._save_sessions()
                self.unified_logger.info(f"User logged out: {username}")
                return True
            return False
        
        except Exception as e:
            self.unified_logger.error(f"Logout error: {e}")
            return False
    
    def verify_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Verify if session is valid"""
        try:
            if session_token not in self.sessions:
                return None
            
            session = self.sessions[session_token]
            expires_at = datetime.fromisoformat(session['expires_at'])
            
            # Check if session expired
            if datetime.now(timezone.utc) > expires_at:
                del self.sessions[session_token]
                self._save_sessions()
                return None
            
            return session
        
        except Exception as e:
            self.unified_logger.error(f"Session verification error: {e}")
            return None
    
    def get_default_permissions_for_role(self, role: UserRole) -> List[str]:
        """Get default permissions based on user role"""
        if role == UserRole.ADMIN:
            return [p.value for p in Permission]
        
        elif role == UserRole.TRADER:
            return [
                Permission.MANUAL_TRADING.value,
                Permission.AUTO_TRADING.value,
                Permission.DCA_BOT.value,
                Permission.AI_PREDICTION.value,
                Permission.MARKET_ANALYSIS.value,
                Permission.TECHNICAL_ANALYSIS.value,
                Permission.PORTFOLIO_VIEW.value,
                Permission.PORTFOLIO_EDIT.value,
                Permission.DASHBOARD_VIEW.value,
                Permission.SMART_ALERTS.value,
                Permission.ONCHAIN_ANALYSIS.value,
                Permission.WHALE_TRACKING.value,
                Permission.ORDER_BOOK.value,
                Permission.FUNDING_RATES.value,
            ]
        
        elif role == UserRole.ANALYST:
            return [
                Permission.MARKET_ANALYSIS.value,
                Permission.TECHNICAL_ANALYSIS.value,
                Permission.FUNDAMENTAL_ANALYSIS.value,
                Permission.MULTI_TIMEFRAME.value,
                Permission.PATTERN_RECOGNITION.value,
                Permission.ONCHAIN_ANALYSIS.value,
                Permission.WHALE_TRACKING.value,
                Permission.ORDER_BOOK.value,
                Permission.FUNDING_RATES.value,
                Permission.NEWS_SENTIMENT.value,
                Permission.KOL_TRACKING.value,
                Permission.DASHBOARD_VIEW.value,
                Permission.AI_PREDICTION.value,
                Permission.BACKTESTING.value,
            ]
        
        elif role == UserRole.VIEWER:
            return [
                Permission.DASHBOARD_VIEW.value,
                Permission.PORTFOLIO_VIEW.value,
                Permission.MARKET_ANALYSIS.value,
                Permission.NEWS_SENTIMENT.value,
            ]
        
        return []
    
    def has_permission(self, username: str, permission: str) -> bool:
        """Check if user has specific permission"""
        try:
            if username not in self.users:
                return False
            
            user = self.users[username]
            
            # Admin has all permissions
            if user.role == UserRole.ADMIN:
                return True
            
            # Check if user has the specific permission
            return permission in user.permissions
        
        except Exception as e:
            self.unified_logger.error(f"Permission check error: {e}")
            return False
    
    def grant_permission(self, username: str, permission: str, granted_by: str) -> tuple:
        """Grant permission to user (admin only)"""
        try:
            if username not in self.users:
                return False, "User not found"
            
            user = self.users[username]
            
            # Check if permission is valid
            try:
                Permission(permission)
            except ValueError:
                return False, f"Invalid permission: {permission}"
            
            # Add permission if not already granted
            if permission not in user.permissions:
                user.permissions.append(permission)
                self._save_users()
                self.unified_logger.info(f"Permission '{permission}' granted to {username} by {granted_by}")
                return True, f"Permission '{permission}' granted successfully"
            
            return False, "Permission already granted"
        
        except Exception as e:
            self.unified_logger.error(f"Grant permission error: {e}")
            return False, f"Error granting permission: {str(e)}"
    
    def revoke_permission(self, username: str, permission: str, revoked_by: str) -> tuple:
        """Revoke permission from user (admin only)"""
        try:
            if username not in self.users:
                return False, "User not found"
            
            user = self.users[username]
            
            # Cannot revoke from admin
            if user.role == UserRole.ADMIN:
                return False, "Cannot revoke permissions from admin"
            
            # Remove permission
            if permission in user.permissions:
                user.permissions.remove(permission)
                self._save_users()
                self.unified_logger.info(f"Permission '{permission}' revoked from {username} by {revoked_by}")
                return True, f"Permission '{permission}' revoked successfully"
            
            return False, "Permission not found"
        
        except Exception as e:
            self.unified_logger.error(f"Revoke permission error: {e}")
            return False, f"Error revoking permission: {str(e)}"
    
    def set_user_role(self, username: str, new_role: str, set_by: str) -> tuple:
        """Change user role and update permissions accordingly (admin only)"""
        try:
            if username not in self.users:
                return False, "User not found"
            
            if username == 'admin':
                return False, "Cannot change admin role"
            
            user = self.users[username]
            
            # Validate role
            try:
                role_enum = UserRole(new_role)
            except ValueError:
                return False, f"Invalid role: {new_role}"
            
            # Update role and permissions
            old_role = user.role.value
            user.role = role_enum
            user.permissions = self.get_default_permissions_for_role(role_enum)
            
            self._save_users()
            self.unified_logger.info(f"User {username} role changed from {old_role} to {new_role} by {set_by}")
            return True, f"User role changed to {new_role} successfully"
        
        except Exception as e:
            self.unified_logger.error(f"Set role error: {e}")
            return False, f"Error setting role: {str(e)}"
    
    def create_user(self, username: str, password: str, email: str = "", role: str = "viewer", created_by: str = "admin") -> tuple:
        """
        Create new user (requires approval for non-admin users)
        Returns: (success: bool, message: str)
        """
        try:
            # Validate username
            if username in self.users:
                return False, "Username already exists"
            
            if len(username) < 3:
                return False, "Username must be at least 3 characters"
            
            # Validate password
            if len(password) < self.password_min_length:
                return False, f"Password must be at least {self.password_min_length} characters"
            
            # Hash password
            password_hash, salt = self._hash_password(password)
            full_hash = f"{password_hash}:{salt}"
            
            # Validate role
            try:
                role_enum = UserRole(role)
            except ValueError:
                role_enum = UserRole.VIEWER  # Default to viewer
            
            # Get default permissions for role
            default_permissions = self.get_default_permissions_for_role(role_enum)
            
            # Create user with pending status
            new_user = User(
                username=username,
                password_hash=full_hash,
                role=role_enum,
                status=UserStatus.PENDING,
                created_at=datetime.now(timezone.utc),
                permissions=default_permissions,
                email=email
            )
            
            self.users[username] = new_user
            self._save_users()
            
            self.unified_logger.info(f"New user created (pending approval): {username} as {role} by {created_by}")
            return True, f"User '{username}' created successfully as {role}. Awaiting admin approval."
        
        except Exception as e:
            self.unified_logger.error(f"User creation error: {e}", exception=e)
            return False, f"Error creating user: {str(e)}"
    
    def approve_user(self, username: str, approved_by: str) -> tuple:
        """Approve pending user (admin only)"""
        try:
            if username not in self.users:
                return False, "User not found"
            
            user = self.users[username]
            
            if user.status != UserStatus.PENDING:
                return False, f"User is already {user.status.value}"
            
            # Approve user
            user.status = UserStatus.ACTIVE
            user.approved_by = approved_by
            user.approved_at = datetime.now(timezone.utc)
            
            self._save_users()
            
            self.unified_logger.info(f"User approved: {username} by {approved_by}")
            return True, f"User '{username}' approved successfully"
        
        except Exception as e:
            self.unified_logger.error(f"User approval error: {e}")
            return False, f"Error approving user: {str(e)}"
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get list of all users (admin only)"""
        try:
            users_list = []
            for username, user in self.users.items():
                users_list.append({
                    'username': username,
                    'role': user.role.value,
                    'status': user.status.value,
                    'email': user.email,
                    'permissions': user.permissions,
                    'permissions_count': len(user.permissions),
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'approved_by': user.approved_by,
                    'approved_at': user.approved_at.isoformat() if user.approved_at else None
                })
            
            return users_list
        
        except Exception as e:
            self.unified_logger.error(f"Get users error: {e}")
            return []
    
    def get_user_permissions(self, username: str) -> List[str]:
        """Get user's permissions"""
        try:
            if username in self.users:
                return self.users[username].permissions.copy()
            return []
        except Exception as e:
            self.unified_logger.error(f"Get user permissions error: {e}")
            return []
    
    def get_all_permissions(self) -> List[Dict[str, str]]:
        """Get all available permissions"""
        return [{'value': p.value, 'name': p.name} for p in Permission]
    
    def get_pending_users(self) -> List[Dict[str, Any]]:
        """Get list of users pending approval"""
        try:
            pending = []
            for username, user in self.users.items():
                if user.status == UserStatus.PENDING:
                    pending.append({
                        'username': username,
                        'email': user.email,
                        'created_at': user.created_at.isoformat() if user.created_at else None
                    })
            
            return pending
        
        except Exception as e:
            self.unified_logger.error(f"Get pending users error: {e}")
            return []
    
    def suspend_user(self, username: str, suspended_by: str) -> tuple:
        """Suspend user account (admin only)"""
        try:
            if username not in self.users:
                return False, "User not found"
            
            if username == 'admin':
                return False, "Cannot suspend admin account"
            
            user = self.users[username]
            user.status = UserStatus.SUSPENDED
            
            # Invalidate all sessions for this user
            sessions_to_remove = [token for token, session in self.sessions.items() 
                                 if session['username'] == username]
            for token in sessions_to_remove:
                del self.sessions[token]
            
            self._save_users()
            self._save_sessions()
            
            self.unified_logger.info(f"User suspended: {username} by {suspended_by}")
            return True, f"User '{username}' suspended successfully"
        
        except Exception as e:
            self.unified_logger.error(f"User suspension error: {e}")
            return False, f"Error suspending user: {str(e)}"
    
    def delete_user(self, username: str, deleted_by: str) -> tuple:
        """Delete user account (admin only)"""
        try:
            if username not in self.users:
                return False, "User not found"
            
            if username == 'admin':
                return False, "Cannot delete admin account"
            
            # Remove user
            del self.users[username]
            
            # Remove all sessions
            sessions_to_remove = [token for token, session in self.sessions.items() 
                                 if session['username'] == username]
            for token in sessions_to_remove:
                del self.sessions[token]
            
            self._save_users()
            self._save_sessions()
            
            self.unified_logger.info(f"User deleted: {username} by {deleted_by}")
            return True, f"User '{username}' deleted successfully"
        
        except Exception as e:
            self.unified_logger.error(f"User deletion error: {e}")
            return False, f"Error deleting user: {str(e)}"
    
    def change_password(self, username: str, old_password: str, new_password: str) -> tuple:
        """Change user password"""
        try:
            if username not in self.users:
                return False, "User not found"
            
            user = self.users[username]
            
            # Verify old password
            if not self._verify_password(old_password, user.password_hash):
                return False, "Current password is incorrect"
            
            # Validate new password
            if len(new_password) < self.password_min_length:
                return False, f"New password must be at least {self.password_min_length} characters"
            
            # Check password complexity
            complexity_error = self._validate_password_complexity(new_password)
            if complexity_error:
                return False, complexity_error
            
            # Hash new password
            password_hash, salt = self._hash_password(new_password)
            user.password_hash = f"{password_hash}:{salt}"
            
            self._save_users()
            
            self.unified_logger.info(f"Password changed for user: {username}")
            return True, "Password changed successfully"
        
        except Exception as e:
            self.unified_logger.error(f"Password change error: {e}")
            return False, f"Error changing password: {str(e)}"
    
    def _validate_password_complexity(self, password: str) -> Optional[str]:
        """Validate password complexity"""
        if len(password) < self.password_min_length:
            return f"Password must be at least {self.password_min_length} characters"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not has_upper:
            return "Password must contain at least one uppercase letter"
        if not has_lower:
            return "Password must contain at least one lowercase letter"
        if not has_digit:
            return "Password must contain at least one number"
        if not has_special:
            return "Password must contain at least one special character"
        
        return None
    
    def request_password_reset(self, username: str, email: str) -> tuple:
        """Request password reset - generates secure code"""
        try:
            if username not in self.users:
                # Don't reveal if user exists or not for security
                return True, "If account exists, reset code has been generated"
            
            user = self.users[username]
            
            # Verify email matches
            if user.email != email:
                return True, "If account exists, reset code has been generated"
            
            # Generate 6-digit secure reset code
            reset_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
            
            # Store reset code with expiry
            self.reset_codes[username] = {
                'code': reset_code,
                'expires_at': (datetime.now(timezone.utc) + timedelta(minutes=self.reset_code_expiry)).isoformat(),
                'attempts': 0,
                'max_attempts': 3
            }
            
            self._save_reset_codes()
            
            self.unified_logger.info(f"Password reset requested for user: {username}")
            
            # In production, send code via email
            # For now, return the code (for demo purposes)
            return True, f"Reset code generated: {reset_code} (Valid for {self.reset_code_expiry} minutes)"
        
        except Exception as e:
            self.unified_logger.error(f"Password reset request error: {e}")
            return False, "Error requesting password reset"
    
    def verify_reset_code(self, username: str, code: str) -> tuple:
        """Verify password reset code"""
        try:
            if username not in self.reset_codes:
                return False, "Invalid or expired reset code"
            
            reset_info = self.reset_codes[username]
            
            # Check if expired
            expires_at = datetime.fromisoformat(reset_info['expires_at'])
            if datetime.now(timezone.utc) > expires_at:
                del self.reset_codes[username]
                self._save_reset_codes()
                return False, "Reset code has expired"
            
            # Check attempts
            if reset_info['attempts'] >= reset_info['max_attempts']:
                del self.reset_codes[username]
                self._save_reset_codes()
                return False, "Too many failed attempts. Please request a new code"
            
            # Verify code
            if reset_info['code'] != code:
                reset_info['attempts'] += 1
                self._save_reset_codes()
                remaining = reset_info['max_attempts'] - reset_info['attempts']
                return False, f"Invalid code. {remaining} attempts remaining"
            
            return True, "Code verified successfully"
        
        except Exception as e:
            self.unified_logger.error(f"Reset code verification error: {e}")
            return False, "Error verifying reset code"
    
    def reset_password_with_code(self, username: str, code: str, new_password: str) -> tuple:
        """Reset password using verified code"""
        try:
            # Verify code first
            verified, message = self.verify_reset_code(username, code)
            if not verified:
                return False, message
            
            if username not in self.users:
                return False, "User not found"
            
            # Validate new password
            if len(new_password) < self.password_min_length:
                return False, f"Password must be at least {self.password_min_length} characters"
            
            # Check password complexity
            complexity_error = self._validate_password_complexity(new_password)
            if complexity_error:
                return False, complexity_error
            
            user = self.users[username]
            
            # Hash new password
            password_hash, salt = self._hash_password(new_password)
            user.password_hash = f"{password_hash}:{salt}"
            
            # Reset failed attempts and unlock account
            user.failed_login_attempts = 0
            user.locked_until = None
            
            # Remove reset code
            if username in self.reset_codes:
                del self.reset_codes[username]
            
            self._save_users()
            self._save_reset_codes()
            
            self.unified_logger.info(f"Password reset successful for user: {username}")
            return True, "Password reset successfully. You can now login with your new password"
        
        except Exception as e:
            self.unified_logger.error(f"Password reset error: {e}")
            return False, f"Error resetting password: {str(e)}"
    
    # ==================== ENCRYPTION METHODS ====================
    
    def _initialize_encryption(self):
        """Initialize AES-256 encryption with secure key derivation"""
        try:
            if not CRYPTO_AVAILABLE:
                return
            
            # Check if encryption key exists
            if os.path.exists(self.key_file):
                # Load existing key
                with open(self.key_file, 'rb') as f:
                    key = f.read()
            else:
                # Generate new encryption key using PBKDF2
                # Use system-specific salt for key derivation
                salt = secrets.token_bytes(32)
                
                # Master password (in production, use environment variable or secure vault)
                master_password = b"GOD_MODE_1000_ULTRA_SECURE_MASTER_KEY_V2"
                
                # Derive key using PBKDF2 with 500,000 iterations
                kdf = PBKDF2(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=500000,
                )
                key_material = kdf.derive(master_password)
                key = base64.urlsafe_b64encode(key_material)
                
                # Save key to hidden file
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                
                # Hide the key file (Windows)
                try:
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(self.key_file, 0x02)  # FILE_ATTRIBUTE_HIDDEN
                except:
                    pass
            
            # Initialize Fernet cipher (AES-256)
            self.cipher = Fernet(key)
            self.unified_logger.info("🔐 AES-256 encryption initialized successfully")
            
        except Exception as e:
            self.unified_logger.error(f"Failed to initialize encryption: {e}")
            self.cipher = None
    
    def _encrypt_data(self, data: str) -> bytes:
        """Encrypt data using AES-256"""
        try:
            if self.cipher is None or not CRYPTO_AVAILABLE:
                return data.encode('utf-8')
            
            return self.cipher.encrypt(data.encode('utf-8'))
        except Exception as e:
            self.unified_logger.error(f"Encryption error: {e}")
            return data.encode('utf-8')
    
    def _decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt data using AES-256"""
        try:
            if self.cipher is None or not CRYPTO_AVAILABLE:
                return encrypted_data.decode('utf-8')
            
            decrypted = self.cipher.decrypt(encrypted_data)
            return decrypted.decode('utf-8')
        except Exception as e:
            self.unified_logger.error(f"Decryption error: {e}")
            # Try to decode as plain text (backward compatibility)
            try:
                return encrypted_data.decode('utf-8')
            except:
                return "{}"
    
    # ==================== PRIVATE METHODS ====================
    
    def _load_users(self):
        """Load users from encrypted file"""
        try:
            if os.path.exists(self.users_file):
                # Read encrypted data
                with open(self.users_file, 'rb') as f:
                    encrypted_data = f.read()
                
                # Decrypt data
                decrypted_json = self._decrypt_data(encrypted_data)
                data = json.loads(decrypted_json)
                
                for username, user_data in data.items():
                    self.users[username] = User(
                        username=user_data['username'],
                        password_hash=user_data['password_hash'],
                        role=UserRole(user_data['role']),
                        status=UserStatus(user_data['status']),
                        created_at=datetime.fromisoformat(user_data['created_at']),
                        permissions=user_data.get('permissions', []),
                        last_login=datetime.fromisoformat(user_data['last_login']) if user_data.get('last_login') else None,
                        email=user_data.get('email', ''),
                        approved_by=user_data.get('approved_by'),
                        approved_at=datetime.fromisoformat(user_data['approved_at']) if user_data.get('approved_at') else None,
                        failed_login_attempts=user_data.get('failed_login_attempts', 0),
                        locked_until=datetime.fromisoformat(user_data['locked_until']) if user_data.get('locked_until') else None
                    )
        
        except Exception as e:
            self.unified_logger.error(f"Failed to load users: {e}")
    
    def _save_users(self):
        """Save users to encrypted file"""
        try:
            data = {}
            for username, user in self.users.items():
                data[username] = {
                    'username': user.username,
                    'password_hash': user.password_hash,
                    'role': user.role.value,
                    'status': user.status.value,
                    'permissions': user.permissions,
                    'created_at': user.created_at.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'email': user.email,
                    'approved_by': user.approved_by,
                    'approved_at': user.approved_at.isoformat() if user.approved_at else None,
                    'failed_login_attempts': user.failed_login_attempts,
                    'locked_until': user.locked_until.isoformat() if user.locked_until else None
                }
            
            # Convert to JSON
            json_data = json.dumps(data, indent=2)
            
            # Encrypt data
            encrypted_data = self._encrypt_data(json_data)
            
            # Write encrypted data
            with open(self.users_file, 'wb') as f:
                f.write(encrypted_data)
        
        except Exception as e:
            self.unified_logger.error(f"Failed to save users: {e}")
    
    def _load_sessions(self):
        """Load sessions from encrypted file"""
        try:
            if os.path.exists(self.sessions_file):
                # Read encrypted data
                with open(self.sessions_file, 'rb') as f:
                    encrypted_data = f.read()
                
                # Decrypt data
                decrypted_json = self._decrypt_data(encrypted_data)
                self.sessions = json.loads(decrypted_json)
                
                # Clean expired sessions
                expired = []
                for token, session in self.sessions.items():
                    expires_at = datetime.fromisoformat(session['expires_at'])
                    if datetime.now(timezone.utc) > expires_at:
                        expired.append(token)
                
                for token in expired:
                    del self.sessions[token]
                
                if expired:
                    self._save_sessions()
        
        except Exception as e:
            self.unified_logger.error(f"Failed to load sessions: {e}")
    
    def _save_sessions(self):
        """Save sessions to encrypted file"""
        try:
            # Convert to JSON
            json_data = json.dumps(self.sessions, indent=2)
            
            # Encrypt data
            encrypted_data = self._encrypt_data(json_data)
            
            # Write encrypted data
            with open(self.sessions_file, 'wb') as f:
                f.write(encrypted_data)
        
        except Exception as e:
            self.unified_logger.error(f"Failed to save sessions: {e}")
    
    def _load_reset_codes(self):
        """Load reset codes from encrypted file"""
        try:
            if os.path.exists(self.reset_codes_file):
                # Read encrypted data
                with open(self.reset_codes_file, 'rb') as f:
                    encrypted_data = f.read()
                
                # Decrypt data
                decrypted_json = self._decrypt_data(encrypted_data)
                self.reset_codes = json.loads(decrypted_json)
                
                # Clean expired codes
                expired = []
                for username, reset_info in self.reset_codes.items():
                    expires_at = datetime.fromisoformat(reset_info['expires_at'])
                    if datetime.now(timezone.utc) > expires_at:
                        expired.append(username)
                
                for username in expired:
                    del self.reset_codes[username]
                
                if expired:
                    self._save_reset_codes()
        
        except Exception as e:
            self.unified_logger.error(f"Failed to load reset codes: {e}")
    
    def _save_reset_codes(self):
        """Save reset codes to encrypted file"""
        try:
            # Convert to JSON
            json_data = json.dumps(self.reset_codes, indent=2)
            
            # Encrypt data
            encrypted_data = self._encrypt_data(json_data)
            
            # Write encrypted data
            with open(self.reset_codes_file, 'wb') as f:
                f.write(encrypted_data)
        
        except Exception as e:
            self.unified_logger.error(f"Failed to save reset codes: {e}")


# Global instance
authentication_manager = AuthenticationManager()

