#dependencies for the application

from app.core.database import SessionLocal

def get_db():
    with SessionLocal() as db:
        yield db