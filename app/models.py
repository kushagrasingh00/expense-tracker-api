from pydantic import BaseModel , ConfigDict , EmailStr 
from datetime import date , datetime
from typing import Optional , List


class category(BaseModel):
    name: str

class CategoryResponse(BaseModel):
    name:str
    model_config = ConfigDict(from_attributes=True)

class ExpenseCreate(BaseModel): 
    title:str
    category_name:Optional[str]
    amount:int
    date: date
    

class ExpenseResponse(BaseModel): 
    id:int
    title:str
    amount:int
    date:date
    created_at:datetime

    model_config = ConfigDict(from_attributes=True)

class UserRegisteration(BaseModel): # what i ask user when they register
    email:EmailStr
    password:str

class UserResponse(BaseModel): # what i give user after they register
    user_id:int
    email:EmailStr
    created_at:datetime

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class TokenData(BaseModel):
    id: Optional[int] = None

class expense_amount(BaseModel):
    amount:int

    model_config = ConfigDict(from_attributes=True)


class token(BaseModel):
    access_token:str
    token_type:str