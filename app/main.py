from fastapi import FastAPI
from app import database_models
from app.database import engine
from .routers import expenses,category,users , auth

app=FastAPI()

database_models.Base.metadata.create_all(bind=engine)  


app.include_router(expenses.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(category.router)


@app.get('/')
def read_root():
    return {'message':'welcome to the task manager'}