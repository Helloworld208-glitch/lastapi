from sqlalchemy.orm  import session




class Fatherclass:
  def __init__(self,session:session):
     self.session=session
  