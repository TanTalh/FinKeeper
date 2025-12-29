from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

# путь к папке data/database
BASE_DIR = Path(__file__).resolve().parent

# путь к файлу БД
DB_PATH = BASE_DIR / "finkeeper.db"

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()