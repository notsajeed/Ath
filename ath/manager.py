import os
import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".ath" / "config.json"

def load_config():
    """Load Ath config file"""
    if not CONFIG_PATH.exists():
        return {"provider": "ollama", "model": "codellama:7b", "api_keys": {}}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"provider": "ollama", "model": "codellama:7b", "api_keys": {}}

def save_config(cfg):
    """Save config file"""
    os.makedirs(CONFIG_PATH.parent, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def get_config_value(key, default=None):
    """Get a specific config value"""
    cfg = load_config()
    return cfg.get(key, default)

def set_config_value(key, value):
    """Set a config value"""
    cfg = load_config()
    if key in ["openai_key", "anthropic_key", "ollama_key"]:
        provider = key.split("_")[0]
        cfg.setdefault("api_keys", {})[provider] = value
    else:
        cfg[key] = value
    save_config(cfg)

def get_api_key(provider):
    """Get API key from config or environment"""
    cfg = load_config()
    api_key = cfg.get("api_keys", {}).get(provider)
    if not api_key:
        env_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "ollama": "OLLAMA_API_KEY"
        }
        api_key = os.getenv(env_map.get(provider, ""), "")
    return api_key

def show_config():
    """Show current config (hide sensitive keys)"""
    cfg = load_config()
    for p, k in cfg.get("api_keys", {}).items():
        cfg["api_keys"][p] = "••••••" if k else ""
    print(json.dumps(cfg, indent=2))
