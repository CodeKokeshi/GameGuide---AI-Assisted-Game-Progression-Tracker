# -*- coding: utf-8 -*-
"""
Data Management Module

Handles all data persistence operations including games, settings,
and encryption functionality.
"""

import json
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class DataManager:
    """Manages data persistence and encryption for the application"""
    
    def __init__(self):
        self.data_file = "game_progress.json"
        self.settings_file = "settings.json"
        self.encryption_key = self._get_encryption_key()
        
    def _get_encryption_key(self):
        """Generate encryption key from a fixed salt"""
        # In production, you might want to store this more securely
        salt = b'game_tracker_salt_2025'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(b'game_progress_tracker_key'))
        return Fernet(key)
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key"""
        if not api_key:
            return ""
        encrypted = self.encryption_key.encrypt(api_key.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key"""
        if not encrypted_key:
            return ""
        try:
            decoded = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted = self.encryption_key.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            print(f"Error decrypting API key: {e}")
            return ""
    
    def load_games(self):
        """Load games from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading games: {e}")
                return {}
        return {}
    
    def save_games(self, games):
        """Save games to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(games, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving games: {e}")
    
    def load_settings(self):
        """Load settings from JSON file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return {"dark_mode": True, "ai_provider": "Gemini", "api_key": ""}
        return {"dark_mode": True, "ai_provider": "Gemini", "api_key": ""}
    
    def save_settings(self, settings):
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_api_key(self, provider):
        """Load API key for the given provider"""
        settings = self.load_settings()
        encrypted_key = settings.get(f"{provider.lower()}_api_key")
        if not encrypted_key:
            # Backwards compatibility for earlier single-key storage
            encrypted_key = settings.get("api_key", "")
        return self.decrypt_api_key(encrypted_key)
    
    def save_api_key(self, provider, api_key):
        """Save API key for the given provider"""
        settings = self.load_settings()
        encrypted_key = self.encrypt_api_key(api_key)
        settings[f"{provider.lower()}_api_key"] = encrypted_key
        # Maintain legacy field for compatibility
        settings["api_key"] = encrypted_key
        self.save_settings(settings)