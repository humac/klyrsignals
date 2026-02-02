from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

import urllib.parse

# Construct DB URL safely from env vars (handling special chars in password)
# Fallback to DATABASE_URL if provided directly (e.g. Heroku), otherwise build it
if os.getenv("DATABASE_URL"):
    DATABASE_URL = os.getenv("DATABASE_URL")
else:
    user = os.getenv("POSTGRES_USER", "klyr_admin")
    password = os.getenv("POSTGRES_PASSWORD", "klyr_secure_password_dev")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "klyrsignals")
    
    encoded_password = urllib.parse.quote_plus(password)
    DATABASE_URL = f"postgresql://{user}:{encoded_password}@{host}:{port}/{db_name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
