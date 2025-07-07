from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from os import getenv

engine = create_engine(getenv("DATABASE_URL"))

def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
