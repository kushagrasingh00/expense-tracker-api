from fastapi import FastAPI,APIRouter,Depends,HTTPException, status 
from app import models , Oauth2
from app.database import get_db 
from sqlalchemy.orm import Session
from app import database_models
from datetime import date
from fastapi import Query
from typing import List



router=APIRouter(
    tags=['Expenses'])


#---------------------------------------------------------------------------------------------------------------

# Creating Expenses
@router.post('/expenses',response_model=models.ExpenseResponse,status_code=status.HTTP_201_CREATED)
def create_expense(expense:models.ExpenseCreate ,db:Session=Depends(get_db),current_user: database_models.UserSchema = Depends(Oauth2.get_current_user)):

    # getting category_id from the user and assigning it to our database 
    # the user will give category in NAME we have to link the name with its ID 
    # the user should only be able to use their own category 
    # The user sends "Food", not the category's ID

    category_name=expense.category_name                    
    category_object=db.query(database_models.CategorySchema).filter(database_models.CategorySchema.name == category_name , database_models.CategorySchema.user_id == current_user.user_id).first() 

    # if the user sets the category to be food - but food does not exist for the user as they never created it , 
    # -> then our category_object will be NONE 
    # we will have to handle it before assigning the id 

    if category_object is None:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='category does not exist')
    
    category_id=category_object.category_id

    # new expense object -> convert pydantic to python dict by model_dump()
    new_expense=database_models.Expenseschema(**expense.model_dump(exclude={"category_name"}), 
    user_id=current_user.user_id , category_id=category_id)

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense

#---------------------------------------------------------------------------------------------------------------

# get all expenses of the user
@router.get('/expenses')
def get_all_expenses(
    sort_by:str| None = None,           # sorting
    page: int = Query(1,ge=1),          # pagination
    limit: int = Query(10,ge=1,le=100), # pagination
    category_name: str | None = None,   # optional query parameter - filter by CATEGORY  
    date:date| None = None,             # optional query parameter - filter by DATE
    min_amount:int|None=None,
    max_amount:int|None=None,

    db:Session=Depends(get_db),
    current_user:database_models.UserSchema=Depends(Oauth2.get_current_user)
    ):
    
    query=db.query(database_models.Expenseschema).filter(database_models.Expenseschema.user_id==current_user.user_id)

    # no need to add user id validation line in each db.query() bcz its already there in the base query

    # category param
    if category_name is not None:
        category=db.query(database_models.CategorySchema).filter(database_models.CategorySchema.name==category_name,database_models.CategorySchema.user_id == current_user.user_id).first()

        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='no category found')

        query=query.filter(database_models.Expenseschema.category_id == category.category_id)

    # date param    
    if date is not None:
        query=query.filter(database_models.Expenseschema.date == date)

    # amt param
    if min_amount is not None:
        query=query.filter(database_models.Expenseschema.amount >= min_amount)

    if max_amount is not None:
        query=query.filter(database_models.Expenseschema.amount <= max_amount)

    # sorting
    if sort_by == 'amount':
        query=query.order_by(database_models.Expenseschema.amount)
        
    if sort_by == "date":
        query = query.order_by(database_models.Expenseschema.date)   

    # pagination
    offset= (page-1)*limit
    query=query.offset(offset).limit(limit) # no need to add .filter -> as its already added in our original query

    expenses=query.all()
    return expenses
# --------------------------------------------------------------------------------------------------------------------------------

# FEATURES 2 

# total spending by the user
@router.get('/expenses/summary')
def total_expenditure(db:Session=Depends(get_db),
    current_user:database_models.UserSchema=Depends(Oauth2.get_current_user)):

    query=db.query(database_models.Expenseschema).filter(database_models.Expenseschema.user_id == current_user.user_id).all()

    total_amount=0
    for i in query:
        total_amount+=i.amount     

    
    return {'detail':f'your total expenditure is {total_amount} Rs'}

# ------------------------------------------------------------------
# FEATURE 2
# spending by category

@router.get('/expenses/summary/category')
def total_expenditure_by_category(category_name:str,db:Session=Depends(get_db),
    current_user:database_models.UserSchema=Depends(Oauth2.get_current_user)):

    category=db.query(database_models.CategorySchema).filter(database_models.CategorySchema.name==category_name,database_models.Expenseschema.user_id == current_user.user_id).first()

    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='no category found')

    category_id=category.category_id

    query=db.query(database_models.Expenseschema).filter(database_models.Expenseschema.category_id==category_id,database_models.Expenseschema.user_id == current_user.user_id).all()

    total_amount=0
    for i in query:
        total_amount+=i.amount

    return {'detail':f'your total expenditure for {category_name} is {total_amount} Rs'}

        # check if category exist -> yes -> look for its id -> assign id to query to get all the expenses -> get amount -> add them

# --------------------------------------------------------------------------------------------------------------------------------

# FEATURE 3
# monthly spending

# month | spent amt

@router.get('/expenses/summary/monthly')
def monthly_expenditure(db:Session=Depends(get_db),
    current_user:database_models.UserSchema=Depends(Oauth2.get_current_user)):

    query=db.query(database_models.Expenseschema).filter(database_models.Expenseschema.user_id == current_user.user_id).all()

    monthly_expense={}

    for expense in query:
        month = (expense.date.month)     # inbuilt fxn of py if the data is of date type -> can do data.month , data.year , data.date -> expense.date.year,

        monthly_expense[month] = monthly_expense.get(month, 0) + expense.amount

    return monthly_expense
    

# ------------------------------------------------------------------

# Get Expenses by Id
@router.get('/expenses/{id}')
def get_all_expense(id:int,db:Session=Depends(get_db),current_user:database_models.UserSchema=Depends(Oauth2.get_current_user)):

    # check if id exists                                    
    expense=db.query(database_models.Expenseschema).filter(database_models.Expenseschema.id == id,database_models.Expenseschema.user_id == current_user.user_id).first() # add the current user liine in this line and remove it from below see if that works or not

    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= f'expense with {id} not found')

    if not expense :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='not authorised perform this step')

    return expense

#---------------------------------------------------------------------------------------------------------------

# updating expenses
@router.put('/expenses/{id}')
def update_expense(id:int , new_expense:models.ExpenseCreate,db:Session=Depends(get_db),
    current_user:database_models.UserSchema=Depends(Oauth2.get_current_user)):

    # checking if expense exist and the user is updating their own expense only
    expense=db.query(database_models.Expenseschema).filter(database_models.Expenseschema.id==id,database_models.Expenseschema.user_id == current_user.user_id).first()

    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= f'expense with {id} not found')

    expense.title= new_expense.title
    expense.amount= new_expense.amount
    expense.date= new_expense.date

    db.commit()
    db.refresh(expense)
        
    return expense

#---------------------------------------------------------------------------------------------------------------

# deleting expense
@router.delete('/expenses/{id}')
def delete_expense(id:int,db:Session=Depends(get_db),
    current_user:database_models.UserSchema=Depends(Oauth2.get_current_user)):

    # check if the id exists and if the owner of the expense is the current logged in user
    expense=db.query(database_models.Expenseschema).filter(database_models.Expenseschema.id==id,database_models.Expenseschema.user_id == current_user.user_id).first()

    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= f'expense with {id} not found')

    db.delete(expense)
    db.commit()

    return {'detail':'expense deleted'}








