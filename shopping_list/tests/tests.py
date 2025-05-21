from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

import pytest

from shopping_list.models import ShoppingList, ShoppingItem


@pytest.mark.django_db
def test_valid_shopping_list_created_returns_201():

    url = reverse("all-shopping-lists")
    data = {"name": "abc"}
    client = APIClient()
    response = client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert ShoppingList.objects.get().name == data["name"]


def test_invalid_shopping_list_payload_returns_400():

    url = reverse("all-shopping-lists")
    data = {"invalid": "a"}
    client = APIClient()
    response = client.post(url, data=data, format="json")

    response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_list_all_shopping_lists_returns_200():
    ShoppingList.objects.create(name="a")
    ShoppingList.objects.create(name="b")

    url = reverse("all-shopping-lists")
    client = APIClient()
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert ShoppingList.objects.count() == 2


@pytest.mark.django_db
def test_retrieve_single_shopping_list_returns_200():
    shopping_list = ShoppingList.objects.create(name="a")

    url = reverse("shopping-list-detail", args=[shopping_list.pk])
    client = APIClient()
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == shopping_list.name


@pytest.mark.django_db
def test_retrieve_shopping_list_include_corresponding_item_returns_200():
    shopping_list = ShoppingList.objects.create(name="abc")
    another_shopping_list = ShoppingList.objects.create(name="xyz")

    ShoppingItem.objects.create(shopping_list=shopping_list, name="a", purchased=False)
    ShoppingItem.objects.create(
        shopping_list=another_shopping_list, name="x", purchased=False
    )

    url = reverse("shopping-list-detail", args=[shopping_list.pk])
    client = APIClient()
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["shopping_items"]) == 1
    assert response.data["shopping_items"][0]["name"] == "a"


@pytest.mark.django_db
def test_delete_shopping_list_returns_204():
    shopping_list = ShoppingList.objects.create(name="a")

    url = reverse("shopping-list-detail", args=[shopping_list.pk])
    client = APIClient()
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_update_shopping_list_valid_payload_returns_200():
    shopping_list = ShoppingList.objects.create(name="abc")

    url = reverse("shopping-list-detail", args=[shopping_list.pk])
    data = {"name": "UpdatedName"}
    client = APIClient()
    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == data["name"]


@pytest.mark.django_db
def test_update_shopping_list_invalid_payload_returns_400():
    shopping_list = ShoppingList.objects.create(name="abc")

    url = reverse("shopping-list-detail", args=[shopping_list.pk])
    data = {"invalid field": "invalid data"}
    client = APIClient()
    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_partial_update_shopping_list_valid_payload_returns_200():
    shopping_list = ShoppingList.objects.create(name="abc")

    url = reverse("shopping-list-detail", args=[shopping_list.pk])
    data = {"name": "UpdatedName"}
    client = APIClient()
    response = client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == data["name"]


@pytest.mark.django_db
def test_partial_update_shopping_list_missing_data_returns_200():
    shopping_list = ShoppingList.objects.create(name="abc")

    url = reverse("shopping-list-detail", args=[shopping_list.pk])
    data = {"something_else": "xyz"}
    client = APIClient()
    response = client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_shopping_item_valid_payload_create_returns_201():
    shopping_list = ShoppingList.objects.create(name="abc")

    url = reverse("add-shopping-item", args=[shopping_list.pk])
    data = {"name": "a", "purchased": False}
    client = APIClient()
    response = client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["id"] is not None


@pytest.mark.django_db
def test_shopping_Item_invalid_payload_create_returns_400():
    shopping_list = ShoppingList.objects.create(name="abc")

    url = reverse("add-shopping-item", args=[shopping_list.pk])
    data = {"invalid data": "invalid data"}
    client = APIClient()
    response = client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_retrieve_shopping_item_returns_200(create_shopping_item):
    shopping_item = create_shopping_item(name="abc")

    url = reverse(
        "shopping-item-detail",
        kwargs={"pk": shopping_item.shopping_list.pk, "item_pk": shopping_item.pk},
    )
    client = APIClient()
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(shopping_item.pk)


@pytest.mark.django_db
def test_update_shopping_item_valid_payload_returns_200(create_shopping_item):
    shopping_item = create_shopping_item(name="abc")

    url = reverse(
        "shopping-item-detail",
        kwargs={"pk": shopping_item.shopping_list.pk, "item_pk": shopping_item.pk},
    )
    data = {"name": "updatedName", "purchased": True}
    client = APIClient()
    response = client.put(url, data=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == data["name"]
    assert response.data["purchased"] == data["purchased"]


@pytest.mark.django_db
def test_update_shopping_item_invalid_payload_returns_400(create_shopping_item):
    shopping_item = create_shopping_item(name="abc")

    url = reverse(
        "shopping-item-detail",
        kwargs={"pk": shopping_item.shopping_list.pk, "item_pk": shopping_item.pk},
    )
    data = {"purchased": True}
    client = APIClient()
    response = client.put(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_partial_update_shopping_item_returns_200(create_shopping_item):
    shopping_item = create_shopping_item(name="abc")

    url = reverse(
        "shopping-item-detail",
        kwargs={"pk": shopping_item.shopping_list.pk, "item_pk": shopping_item.pk},
    )
    data = {"purchased": True}
    client = APIClient()
    response = client.patch(url, data=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["purchased"] is True


@pytest.mark.django_db
def test_delete_shopping_item_returns_204(create_shopping_item):
    shopping_item = create_shopping_item(name="abc")

    url = reverse(
        "shopping-item-detail",
        kwargs={"pk": shopping_item.shopping_list.pk, "item_pk": shopping_item.pk},
    )
    client = APIClient()
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
