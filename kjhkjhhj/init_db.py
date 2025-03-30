from database import Base, engine
from user import Userr

def createtables():
   Base.metadata.create_all(bind=engine)

   