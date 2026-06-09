import os
import json
from typing import List, Any
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Settings:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self._config = json.load(f)
        
        # App settings
        self.app_name = self._get_env("SFA_APP_NAME", self._config["app"]["name"])
        self.app_version = self._get_env("SFA_APP_VERSION", self._config["app"]["version"])
        self.debug = self._get_env("SFA_DEBUG", self._config["app"]["debug"], type_cast=bool)

        # Server settings
        self.server_host = self._get_env("SFA_SERVER_HOST", self._config["server"]["host"])
        self.server_port = self._get_env("SFA_SERVER_PORT", self._config["server"]["port"], type_cast=int)
        self.server_reload = self._get_env("SFA_SERVER_RELOAD", self._config["server"]["reload"], type_cast=bool)

        # Database settings
        self.db_type = self._config["database"]["type"]
        self.db_path = self._get_env("SFA_DB_PATH", self._config["database"]["path"])

        # Auth settings
        self.secret_key = self._get_env("SFA_SECRET_KEY", self._config["auth"]["secret_key"])
        self.auth_algorithm = self._get_env("SFA_AUTH_ALGORITHM", self._config["auth"]["algorithm"])
        self.access_token_expire_minutes = self._get_env(
            "SFA_ACCESS_TOKEN_EXPIRE_MINUTES", 
            self._config["auth"]["access_token_expire_minutes"],
            type_cast=int
        )

        # CORS settings
        self.cors_origins = self._get_env("SFA_CORS_ORIGINS", self._config["cors"]["origins"], type_cast=list)
        self.cors_methods = self._config["cors"]["methods"]
        self.cors_headers = self._config["cors"]["headers"]

        # Cloudinary settings
        self.cloudinary_cloud_name = self._get_env("SFA_CLOUDINARY_CLOUD_NAME", self._config["cloudinary"]["cloud_name"])
        self.cloudinary_api_key = self._get_env("SFA_CLOUDINARY_API_KEY", self._config["cloudinary"]["api_key"])
        self.cloudinary_api_secret = self._get_env("SFA_CLOUDINARY_API_SECRET", self._config["cloudinary"]["api_secret"])

    def _get_env(self, key: str, default: Any, type_cast: type = str) -> Any:
        val = os.environ.get(key)
        if val is None:
            return default
        
        if type_cast == bool:
            return val.lower() in ("true", "1", "yes")
        if type_cast == int:
            return int(val)
        if type_cast == list:
            # Handle comma-separated list for origins
            return [item.strip() for item in val.split(",")]
        return val

# Singleton instance
_config_path = os.path.join(os.path.dirname(__file__), "config.json")
settings = Settings(_config_path)
