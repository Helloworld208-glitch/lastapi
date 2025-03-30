from bcrypt import checkpw , hashpw, gensalt





class encrypt:

    @staticmethod
    def testing_password(password:str, hashed_password:str):
        return checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
       



    @staticmethod
    def hash_passwords(password: str):
        return hashpw(password.encode("utf-8"),gensalt() ).decode("utf-8")