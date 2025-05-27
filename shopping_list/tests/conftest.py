from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from shopping_list.models import ShoppingList, ShoppingItem

import pytest

User = get_user_model()


@pytest.fixture(scope="session")
def create_user():
    def _create_user():
        return User.objects.create_user("normalUser", "normal@user.com", "something")

    return _create_user


@pytest.fixture(scope="session")
def create_authenticated_client():
    def _create_authenticated_client(user):
        client = APIClient()
        client.force_login(user)
        return client

    return _create_authenticated_client


@pytest.fixture(scope="session")
def create_shopping_item():
    def _create_shopping_item(name):
        shopping_list = ShoppingList.objects.create(name="my list")
        shopping_item = ShoppingItem.objects.create(
            name=name, purchased=True, shopping_list_id=shopping_list.id
        )
        return shopping_item

    return _create_shopping_item
