from fastapi import FastAPI
import pytest
from app.main import app , database_models
from starlette.testclient import TestClient as TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.database import get_db
from app.utils import pwd_context
from app.Oauth2 import create_token
from app import models

# creating a new db and connecting it to our testing file -> so the dev db reamins seperate from testing db
db_url="postgresql://postgres:1105@localhost:5432/Expense Manager Test"
engine=create_engine(db_url)

testing_session=sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base=declarative_base()

@pytest.fixture()
def session():
    # drop all the previous tables in the databse
    database_models.Base.metadata.drop_all(bind=engine) 
    # create new table
    database_models.Base.metadata.create_all(bind=engine)

    db=testing_session()  
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


# fixture for creating a user   - firxture is a fnx that run before the test runs
@pytest.fixture()
def test_user(session):
    # hashing the password as login requires a hashed password  
    password='pass123'

    hashed_password=pwd_context.hash(password)

    user=database_models.UserSchema(
        email='testuser@gmail.com',
        password=hashed_password
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # returning user is imp as 
    return user


# fixture for creating token -> imp for testing protected routes
@pytest.fixture()
def token(test_user):
    return create_token({"user_id":test_user.user_id})

# fixture for adding the token to request header 
@pytest.fixture
def authorized_client(client,token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

# creating dummy expenses in our databses 
@pytest.fixture()
def expenses(test_user, session):

    expenses_data = [
        {
            "title": "LUNCH",
            "amount": 2500,
            "date": "2026-11-25"
        },
        {
            "title": "DINNER",
            "amount": 6000,
            "date": "2026-04-21"
        }
    ]

    expenses = []

    for expense in expenses_data:
        expense_model = database_models.Expenseschema(
            title=expense["title"],
            amount=expense["amount"],
            date=expense["date"],
            user_id=test_user.user_id
        )

        expenses.append(expense_model)

    session.add_all(expenses)
    session.commit()

    return expenses