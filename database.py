import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

# Use SQLite for local development (much more reliable)
# Use PostgreSQL only when DATABASE_URL is set (i.e. on Render)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Production / Render
    print("Using PostgreSQL (Render)")
    engine = create_engine(DATABASE_URL)
else:
    # Local development
    print("Using SQLite for local development")
    DATABASE_URL = "sqlite:///./dev.db"
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()