from fastapi import FastAPI,status
import pytest
from app import models

from fastapi.middleware.cors import CORSMiddleware
import jwt 
from app.Oauth2 import SECRET,ALGORITHM


def test_create_user(client):
    response=client.post(
        '/register', json = {"email":"tester@gmail.com","password":"pass123"})

    # this line is usefull for validating the response body -- can be removed test would still work 
    new_user = models.UserResponse(**response.json())
 
    assert new_user.email == "tester@gmail.com"
    assert response.status_code == 201

def test_login_user(client,test_user):
    response=client.post(
        '/login',
        json={
            "email": test_user.email, 
            "password": "pass123"})
        # this body goes to our api endpoint and there the actual validation is done 
        # like checking for user and verifying password -> thoink of this like how we send body credentials in postman and we get back a jwt token
        
    assert response.status_code == 200  

    # JWT authentication
    
    # Convert the login response into our 'Token' Pydantic model
    # so we can access the 'access_token' and 'token_type' cleanly.
    login_result=models.token(**response.json())

    payload = jwt.decode(login_result.access_token,SECRET,algorithms=[ALGORITHM]) 

    # payload consists of - user_id and exp

    assert payload.get("user_id") == test_user.user_id
    assert payload.get("exp") is not None
    assert login_result.token_type == "bearer"


# parameterizing imputs -> as we are testing multiple inputs at once
@pytest.mark.parametrize("email,password,status_code",[
    ('wrongemail@gmail.com','pass123',401),
    ('testuser@gmail.com','wrongpass',401),
    ('wrongemail@gmail.com','wrongpass',401),
    (None,'pass123',422),
    ('testuser@gmail.com',None,422)])

def test_login_wrong_password(client,test_user,email,password,status_code):
    response = client.post(
        '/login',
        json={"email":email, "password": password})

    assert response.status_code == status_code
    

