# app/database.py
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# L'URL vient de l'environnement : docker compose la fournit,
# les tests utilisent SQLite.
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://admin:admin123@localhost:5432/senalert"
)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
