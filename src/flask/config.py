"""
Central config for the Time-Capsule Flask app.

Resolution order for every value:
  1. Environment variable  -> used in Lambda / container (prod)
  2. Local gitignored fallback files (temp_secrets.py, firebase_config.py,
     firebaseAdminConfig.json, cf_private_key.pem) -> `python routes.py` dev

Large secrets (Firebase admin JSON, CloudFront private key) exceed Lambda's 4KB
env-var limit, so in Lambda they come from SSM Parameter Store (SecureString),
fetched once per cold start and cached. Locally they are read from disk.
"""

import os

# --- local fallbacks (absent in the container image) -------------------------
try:
    import temp_secrets as _ts
except ImportError:
    _ts = None

try:
    import firebase_config as _fc
except ImportError:
    _fc = None


def _get(name, default=None, local=None):
    val = os.environ.get(name)
    if val is not None:
        return val
    if local is not None:
        return local
    return default


# --- small config values (env, with local fallback) -------------------------
FLASK_SECRET_KEY = _get("FLASK_SECRET_KEY", local=getattr(_ts, "FLASK_SECRET_KEY", None))
PUBLIC_KEY_ID = _get("PUBLIC_KEY_ID", local=getattr(_ts, "PUBLIC_KEY_ID", None))
CFD_BASE_URL = _get("CFD_BASE_URL", default="https://dazfl01h50k5a.cloudfront.net")
BUCKET_NAME = _get("BUCKET_NAME", default="time-capsule-media")

# Lambda injects AWS_REGION into the environment; default for local dev.
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# --- Pyrebase web config (env fields, fallback to firebase_config.config) ----
_FIREBASE_ENV_KEYS = {
    "apiKey": "FIREBASE_API_KEY",
    "authDomain": "FIREBASE_AUTH_DOMAIN",
    "databaseURL": "FIREBASE_DATABASE_URL",
    "projectId": "FIREBASE_PROJECT_ID",
    "storageBucket": "FIREBASE_STORAGE_BUCKET",
    "messagingSenderId": "FIREBASE_MESSAGING_SENDER_ID",
    "appId": "FIREBASE_APP_ID",
    "measurementId": "FIREBASE_MEASUREMENT_ID",
}


def _build_pyrebase_config():
    if os.environ.get("FIREBASE_API_KEY"):
        return {k: os.environ.get(env, "") for k, env in _FIREBASE_ENV_KEYS.items()}
    if _fc is not None:
        return _fc.config
    raise RuntimeError(
        "No Firebase web config found: set FIREBASE_* env vars or provide firebase_config.py"
    )


PYREBASE_CONFIG = _build_pyrebase_config()

# --- large secrets: SSM in Lambda, local files otherwise --------------------
_IN_LAMBDA = bool(os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
_ssm_client = None
_secret_cache = {}

_HERE = os.path.dirname(os.path.abspath(__file__))
_LOCAL_ADMIN_JSON = os.path.join(_HERE, "firebaseAdminConfig.json")
_LOCAL_CF_KEY = getattr(_ts, "PATH_TO_LOCAL_PRIVATE_KEY", "") or os.path.join(_HERE, "cf_private_key.pem")
if not os.path.exists(_LOCAL_CF_KEY):
    _LOCAL_CF_KEY = os.path.join(_HERE, "cf_private_key.pem")


def _ssm():
    global _ssm_client
    if _ssm_client is None:
        import boto3
        _ssm_client = boto3.client("ssm", region_name=AWS_REGION)
    return _ssm_client


def _get_secret(env_name, ssm_param, local_path):
    inline = os.environ.get(env_name)
    if inline:
        return inline
    if ssm_param in _secret_cache:
        return _secret_cache[ssm_param]
    if _IN_LAMBDA or os.environ.get("USE_SSM"):
        value = _ssm().get_parameter(Name=ssm_param, WithDecryption=True)["Parameter"]["Value"]
    else:
        with open(local_path, "r") as f:
            value = f.read()
    _secret_cache[ssm_param] = value
    return value


def get_firebase_admin_json():
    return _get_secret("FIREBASE_ADMIN_JSON", "/time-capsule/firebase-admin-json", _LOCAL_ADMIN_JSON)


def get_cf_private_key_pem():
    return _get_secret("CF_PRIVATE_KEY_PEM", "/time-capsule/cf-private-key", _LOCAL_CF_KEY)
