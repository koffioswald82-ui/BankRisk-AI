"""
Configuration centrale — charge les YAML et expose les constantes.

Toute valeur business vient de config/fraud.yaml ou config/credit.yaml.
Ne jamais mettre de valeurs hardcodées ici.
"""
from pathlib import Path
import yaml

# ── Chemins projet ────────────────────────────────────────────────────────────
ROOT           = Path(__file__).resolve().parent.parent

DATA_RAW       = ROOT / "data" / "raw"
DATA_INTERIM   = ROOT / "data" / "interim"
DATA_PROCESSED = ROOT / "data" / "processed"

MODELS_DIR     = ROOT / "models"
REPORTS_DIR    = ROOT / "reports"
FIGURES_DIR    = REPORTS_DIR / "figures"
METRICS_DIR    = REPORTS_DIR / "metrics"

CONFIG_DIR     = ROOT / "config"
REGISTRY_PATH  = MODELS_DIR / "registry.json"

# ── Loaders YAML ──────────────────────────────────────────────────────────────

def _load(name: str) -> dict:
    path = CONFIG_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"Config introuvable : {path}\n"
            f"Créez le fichier config/{name}.yaml"
        )
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_fraud_config()  -> dict: return _load("fraud")
def get_credit_config() -> dict: return _load("credit")


# ── Accès direct aux chemins de dataset (depuis YAML) ────────────────────────

def fraud_raw_path()  -> Path:
    cfg = get_fraud_config()
    return DATA_RAW / cfg["dataset"]["file"]

def credit_raw_path() -> Path:
    cfg = get_credit_config()
    return DATA_RAW / cfg["dataset"]["file"]

def fraud_model_path()  -> Path: return MODELS_DIR / "fraud_champion.joblib"
def credit_model_path() -> Path: return MODELS_DIR / "credit_champion.joblib"

def fraud_preprocessor_path()  -> Path: return MODELS_DIR / "fraud_preprocessor.joblib"
def credit_preprocessor_path() -> Path: return MODELS_DIR / "credit_preprocessor.joblib"


# ── Constantes d'entraînement (partagées) ────────────────────────────────────
RANDOM_STATE = 42
CV_FOLDS     = 5
