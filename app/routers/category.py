from fastapi import APIRouter,Depends,HTTPException, status 
from app import models , Oauth2
from app.database import get_db 
from sqlalchemy.orm import Session
from app import database_models
from sqlalchemy.exc import IntegrityError
from typing import List

router=APIRouter(
    tags=['categories'])

# ----------------------------------------------------------------------------------------------------------------
# create category -> logged in user only
@router.post('/category',status_code=status.HTTP_201_CREATED)
def create_category(data:models.category,db:Session=Depends(get_db),current_user:database_models.UserSchema = Depends(Oauth2.get_current_user)):

    try:
        new_category=database_models.CategorySchema(**data.model_dump(),user_id=current_user.user_id)

        db.add(new_category)
        db.commit()
        db.refresh(new_category)

        return new_category

    # if the category exists instead of giving an internal server error we handle the error
    except IntegrityError:
        db.rollback()   # rollback() basically means "undo the current database transaction and return the database session to a clean state."
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail='category already exists')



# ----------------------------------------------------------------------------------------------------------------

# list of all the categories created by the user
@router.get('/category',response_model=List[models.CategoryResponse]) # as the response is LIST type we have to mention it otherwise fastapi wants a json response so throws an error
def get_category(db:Session=Depends(get_db),current_user:database_models.UserSchema = Depends(Oauth2.get_current_user)):

    # check if the user has any categories
    list_categories=db.query(database_models.CategorySchema).filter(database_models.CategorySchema.user_id == current_user.user_id).all() # this will return a list 
    
    if len(list_categories)==0 : 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='user has no listed categories')

    return list_categories

# ----------------------------------------------------------------------------------------------------------------

# update category

# check if owner has any category -> yes  -> continue -> user gives category name -> make that name the new name 

@router.put('/category/{category_name}')
def update_category(category_name:str,data:models.category,db:Session=Depends(get_db),current_user:database_models.UserSchema = Depends(Oauth2.get_current_user)):

    category=db.query(database_models.CategorySchema).filter(database_models.CategorySchema.name == category_name , database_models.CategorySchema.user_id == current_user.user_id).first()

    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='no category found')
    
    category.name=data.name

    db.commit()
    db.refresh(category)

    return {'detail':'successfully updated!'} 

# ----------------------------------------------------------------------------------------------------------------

# delete category

@router.delete('/category/{category_name}')
def delete_category(category_name:str,db:Session=Depends(get_db),current_user:database_models.UserSchema = Depends(Oauth2.get_current_user)):

    category=db.query(database_models.CategorySchema).filter(
        database_models.CategorySchema.name == category_name , 
        database_models.CategorySchema.user_id == current_user.user_id).first()

    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='category not found')

    db.delete(category)
    db.commit()

    return {'detail':'category deleted successfully!'}




