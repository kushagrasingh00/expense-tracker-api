from pwdlib import PasswordHash

pwd_context=PasswordHash.recommended()

# hashing password
def hashing_password(password:str):
    return  pwd_context.hash(password)

# verifying passowrd
def verify_password(given_pass,actual_pass):
    return pwd_context.verify(given_pass,actual_pass)