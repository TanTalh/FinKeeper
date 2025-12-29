from data.database.db import engine, Base

def init_db():
    Base.metadata.create_all(bind=engine)