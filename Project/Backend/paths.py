from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent
REPO_ROOT = PROJECT_DIR.parent

FRONTEND_TEMPLATES_DIR = PROJECT_DIR / "frontend" / "templates"
FRONTEND_STATIC_DIR = PROJECT_DIR / "frontend" / "static"

DATA_DIR = REPO_ROOT / "data"
UPLOADS_DIR = REPO_ROOT / "uploads"
STORED_RESUMES_DIR = REPO_ROOT / "stored_resumes"

DB_PATH = DATA_DIR / "app.db"
RESUME_CSV_PATH = DATA_DIR / "archive (1)" / "Resume" / "Resume.csv"
