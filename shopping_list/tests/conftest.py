from shopping_list.models import ShoppingList, ShoppingItem

import pytest


@pytest.fixture(scope="session")
def create_shopping_item():
    def _create_shopping_item(name):
        shopping_list = ShoppingList.objects.create(name="my list")
        shopping_item = ShoppingItem.objects.create(
            name=name, purchased=True, shopping_list_id=shopping_list.id
        )
        return shopping_item

    return _create_shopping_item
