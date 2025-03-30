from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from decouple import config







dburl=config("dburl")
engine = create_engine(dburl)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
def get_db():
     try:
         db=SessionLocal()
         yield db
     finally:
         db.close() 
    
        