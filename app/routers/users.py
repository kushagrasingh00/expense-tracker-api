from fastapi import APIRouter,Depends,HTTPException, status 
from app import models
from app.database import get_db 
from sqlalchemy.orm import Session
from app import database_models
from app.utils import hashing_password 

router=APIRouter(tags=['register'])

# register new user
@router.post('/register',response_model=models.UserResponse,status_code=status.HTTP_201_CREATED)
def register_user(user_credentials:models.UserRegisteration,db:Session=Depends(get_db)):

    # check if the email already exists
    user=db.query(database_models.UserSchema).filter(database_models.UserSchema.email == user_credentials.email).first()

    # if user found
    if user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail='user with email already exists')

    # hash password
    hash=hashing_password(user_credentials.password)
    user_credentials.password=hash
    
    # if no user exists
    new_user=database_models.UserSchema(**user_credentials.model_dump())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

