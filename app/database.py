from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import Request
import os
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost/postgres")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db(request: Request):
    db = SessionLocal()
    db.info["user"] = getattr(request.state, "user_id", None)
    try:
        yield db
    finally:
        db.close()
