# database/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Путь к локальной базе (файл в том же каталоге, где запускается main.py)
DATABASE_URL = "sqlite:///finkeeper.db"

# engine
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

# сессия
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# базовый класс
Base = declarative_base()
