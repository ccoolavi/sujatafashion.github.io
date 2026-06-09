import os
from backend.config import settings

def test_config():
    print(f"App Name: {settings.app_name}")
    print(f"Secret Key: {settings.secret_key}")
    print(f"CORS Origins: {settings.cors_origins}")
    print(f"Server Port: {settings.server_port}")

if __name__ == "__main__":
    # Test 1: Default from JSON
    print("--- Testing Default Config ---")
    test_config()

    # Test 2: Override with Env Vars
    print("\n--- Testing Env Var Overrides ---")
    os.environ["SFA_APP_NAME"] = "Test App"
    os.environ["SFA_SECRET_KEY"] = "super-secret-env-key"
    os.environ["SFA_CORS_ORIGINS"] = "http://localhost:3000,https://sajata.com"
    os.environ["SFA_SERVER_PORT"] = "9000"
    
    # Re-initialize settings for testing (since it's a singleton)
    from backend.config import Settings
    import os
    _config_path = os.path.join(os.path.dirname(__file__), "backend/config.json")
    settings = Settings(_config_path)
    
    test_config()

if __name__ == "__main__":
    # Re-defined to allow testing logic within same file
    pass
