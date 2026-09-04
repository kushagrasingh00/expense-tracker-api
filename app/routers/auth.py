from fastapi import FastAPI,APIRouter,Depends,HTTPException, status 
from app import models , Oauth2
from app.database import get_db 
from sqlalchemy.orm import Session
from app import database_models
from app.utils import verify_password


router=APIRouter(tags=['login'])

# login user
@router.post('/login')
def user_login(user_credentials:models.UserLogin,db:Session=Depends(get_db)):
    # check if email exists
    user=db.query(database_models.UserSchema).filter(database_models.UserSchema.email == user_credentials.email).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='invalid credentials')
    
    # verify password
    password=verify_password(user_credentials.password,user.password)

    if not password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='invalid credentials')

    # create and return token
    access_token=Oauth2.create_token(data={'user_id':user.user_id}) # user is the variable used above we take its user_id from it

    return {"access_token": access_token,"token_type": "bearer"}

