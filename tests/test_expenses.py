import pytest
from app import models


def test_get_all_expenses(authorized_client,expenses):
    response=authorized_client.get('/expenses')
    print(response.json())
    assert response.status_code == 200
    