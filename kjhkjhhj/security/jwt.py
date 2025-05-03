import jwt 
import time
from decouple import config
JWT_SECRET = config("JWT_SECRET")
JWT_ALGO = config("JWT_ALGO")

class jwtclass:
    @staticmethod
    def jwt_gen(user_id:int)->str:
        payload ={ "user_id":user_id , "exp":time.time()+2592000 }


        return jwt.encode(payload,JWT_SECRET,algorithm=JWT_ALGO)
    

    @staticmethod
    def chk_token(token:str)->dict:
        try:
            token= jwt.decode(token,JWT_SECRET,algorithms=[JWT_ALGO])
            if(time.time()>token["exp"]):
                return None
            else:
                return token
        except:
            print("error")
            return None
    @staticmethod
    def jwt_gen_admin(user_id:int)->str:
        payload ={ "user_id":user_id , "exp":time.time()+9000 ,"role":"admin"}


        return jwt.encode(payload,JWT_SECRET,algorithm=JWT_ALGO)
    
            
            
