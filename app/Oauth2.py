import os
from fastapi import Depends,HTTPException, status 
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import database , models , database_models
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login') # extracts the token from teh user request

SECRET = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
TOKEN_EXPIRE_TIME = 30

def create_token(data:dict):

    to_encode=data.copy()
    # add time
    expire=datetime.now()+timedelta(minutes=TOKEN_EXPIRE_TIME)
    #update time 
    to_encode.update({'exp':expire})
    # encode
    encoded_jwt=jwt.encode(to_encode,SECRET,algorithm=ALGORITHM)

    return encoded_jwt

# ---------------------------------------------------------
# Verify the JWT and extract the user ID
# ---------------------------------------------------------
def verify_access_token(token: str, credentials_exception):
    try:
        # Decode the JWT using our secret key
        payload = jwt.decode(
            token,
            SECRET,
            algorithms=[ALGORITHM])
        
        # Get the user ID stored inside the JWT
        user_id = payload.get("user_id")

        # If the JWT doesn't contain a user ID, reject it
        if user_id is None:
            raise credentials_exception

        # Put the user ID into our Pydantic model
        token_data = models.TokenData(id=user_id)

    # If the JWT is invalid/expired/etc.
    except JWTError:
        raise credentials_exception
    
    # Return the verified user information
    return token_data

# ---------------------------------------------------------
# Get the currently logged-in user
# ---------------------------------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db)):

    # Error we will use if authentication fails
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})

    # Verify the JWT
    # Returns TokenData(id=user_id)
    token_data = verify_access_token(token,credentials_exception)

    # Use the ID from the verified token
    # to find the actual user in the database
    user = db.query(database_models.UserSchema).filter(database_models.UserSchema.user_id == token_data.id).first()

    # Return the actual database user
    return user


        
    