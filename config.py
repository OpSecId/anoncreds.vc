import os
import secrets
from pathlib import Path
from dotenv import load_dotenv
from cachelib.file import FileSystemCache
import yaml

load_dotenv()
Path("session").mkdir(parents=True, exist_ok=True)

_CONFIG_DIR = Path(__file__).resolve().parent
_DEMO_CONFIG = Path(os.getenv("DEMO_CONFIG", _CONFIG_DIR / "config.yaml"))


def _load_demo():
    with _DEMO_CONFIG.open() as demo_file:
        demo = yaml.safe_load(demo_file)["demo"]

    predicates = demo.get("presentation", {}).get("predicate") or {}
    if isinstance(predicates, dict) and predicates:
        name, (expression, value) = next(iter(predicates.items()))
        demo["presentation"]["predicate"] = [name, expression, value]
    return demo


class Config(object):
    APP_TITLE = "AnonCreds + WebVH"

    DOMAIN = os.getenv("DOMAIN", "localhost:5000")
    ENDPOINT = f"http://{DOMAIN}" if DOMAIN == "localhost:5000" else f"https://{DOMAIN}"

    ASKAR_DB = os.getenv("ASKAR_DB", "sqlite://app.db")

    SESSION_TYPE = "cachelib"
    SESSION_SERIALIZATION_FORMAT = "json"
    SESSION_CACHELIB = FileSystemCache(threshold=500, cache_dir="session")
    SESSION_COOKIE_NAME = "AnonCreds"
    SESSION_COOKIE_SAMESITE = "Strict"
    SESSION_COOKIE_HTTPONLY = "True"

    AGENT_MODE = os.getenv("AGENT_MODE", "single")
    AGENT_ADMIN_API_KEY = os.getenv("AGENT_ADMIN_API_KEY")
    AGENT_ADMIN_ENDPOINT = os.getenv("AGENT_ADMIN_ENDPOINT")

    WEBVH_SERVER = os.getenv("WEBVH_SERVER", None)

    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(16))

    DEMO = _load_demo()
