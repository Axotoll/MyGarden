from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".dev.env")

MONGO_DB_URI = os.getenv("MONGO_DB_URI")
JWT_SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")