from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

import pytest

from shopping_list.models import ShoppingList, ShoppingItem


@pytest.mark.django_db
class TestShoppingList:

    def test_valid_shopping_list_created_returns_201(
        self, create_user, create_authenticated_client
    ):

        url = reverse("all-shopping-lists")
        data = {"name": "abc"}
        client = create_authenticated_client(create_user())
        response = client.post(url, data=data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert ShoppingList.objects.get().name == data["name"]

    def test_invalid_shopping_list_payload_returns_400(
        self, create_user, create_authenticated_client
    ):
        user = create_user()

        url = reverse("all-shopping-lists")
        data = {"invalid": "a"}
        client = create_authenticated_client(user)
        response = client.post(url, data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_all_shopping_lists_returns_200(
        self, create_user, create_authenticated_client, create_shopping_list
    ):
        user = create_user()
        create_shopping_list(name="a", user=user)
        create_shopping_list(name="b", user=user)

        url = reverse("all-shopping-lists")
        client = create_authenticated_client(user)
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert ShoppingList.objects.count() == 2

    def test_retrieve_single_shopping_list_returns_200(
        self, create_user, create_authenticated_client, create_shopping_list
    ):
        user = create_user()
        shopping_list = create_shopping_list(name="a", user=user)

        url = reverse("shopping-list-detail", args=[shopping_list.pk])
        client = create_authenticated_client(user)
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == shopping_list.name

    def test_retrieve_shopping_list_include_corresponding_item_returns_200(
        self, create_user, create_authenticated_client, create_shopping_list
    ):
        user = create_user()
        shopping_list = create_shopping_list(name="abc", user=user)
        another_shopping_list = create_shopping_list(name="xyz", user=user)

        ShoppingItem.objects.create(
            shopping_list=shopping_list, name="a", purchased=False
        )
        ShoppingItem.objects.create(
            shopping_list=another_shopping_list, name="x", purchased=False
        )

        url = reverse("shopping-list-detail", args=[shopping_list.pk])
        client = create_authenticated_client(user)
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["shopping_items"]) == 1
        assert response.data["shopping_items"][0]["name"] == "a"

    def test_delete_shopping_list_returns_204(
        self, create_user, create_authenticated_client, create_shopping_list
    ):
        user = create_user()
        client = create_authenticated_client(user)
        shopping_list = create_shopping_list(name="abc", user=user)

        url = reverse("shopping-list-detail", args=[shopping_list.pk])
        response = client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_update_shopping_list_valid_payload_returns_200(
        self, create_user, create_shopping_list, create_authenticated_client
    ):
        user = create_user()
        shopping_list = create_shopping_list(name="abc", user=user)

        url = reverse("shopping-list-detail", args=[shopping_list.pk])
        data = {"name": "UpdatedName"}
        client = create_authenticated_client(user)
        response = client.put(url, data=data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == data["name"]

    def test_update_shopping_list_invalid_payload_returns_400(
        self, create_user, create_shopping_list, create_authenticated_client
    ):
        user = create_user()
        shopping_list = create_shopping_list(name="abc", user=user)

        url = reverse("shopping-list-detail", args=[shopping_list.pk])
        data = {"invalid field": "invalid data"}
        client = create_authenticated_client(user)
        response = client.put(url, data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_partial_update_shopping_list_valid_payload_returns_200(
        self, create_user, create_shopping_list, create_authenticated_client
    ):
        user = create_user()
        shopping_list = create_shopping_list(name="abc", user=user)

        url = reverse("shopping-list-detail", args=[shopping_list.pk])
        data = {"name": "UpdatedName"}
        client = create_authenticated_client(user)
        response = client.patch(url, data=data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == data["name"]

    def test_partial_update_shopping_list_missing_data_returns_200(
        self, create_user, create_shopping_list, create_authenticated_client
    ):
        user = create_user()
        shopping_list = create_shopping_list(name="abc", user=user)

        url = reverse("shopping-list-detail", args=[shopping_list.pk])
        data = {"something_else": "xyz"}
        client = create_authenticated_client(user)
        response = client.patch(url, data=data, format="json")

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestShoppingItem:
    def test_shopping_item_valid_payload_create_returns_201(
        self, create_user, create_shopping_list, create_authenticated_client
    ):
        user = create_user()
        shopping_list = create_shopping_list(name="a", user=user)

        url = reverse("add-shopping-item", args=[shopping_list.pk])
        data = {"name": "a", "purchased": False}
        client = create_authenticated_client(user)
        response = client.post(url, data=data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] is not None

    def test_shopping_Item_invalid_payload_create_returns_400(
        self, create_user, create_shopping_list, create_authenticated_client
    ):
        user = create_user()
        shopping_list = create_shopping_list(name="a", user=user)

        url = reverse("add-shopping-item", args=[shopping_list.pk])
        data = {"invalid data": "invalid data"}
        client = create_authenticated_client(user)
        response = client.post(url, data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_shopping_item_returns_200(
        self, create_shopping_item, create_user, create_authenticated_client
    ):
        user = create_user()
        client = create_authenticated_client(user)
        shopping_item = create_shopping_item(name="abc", user=user)

        url = reverse(
            "shopping-item-detail",
            kwargs={"pk": shopping_item.shopping_list.pk, "item_pk": shopping_item.pk},
        )
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(shopping_item.pk)

    def test_update_shopping_item_valid_payload_returns_200(
        self, create_shopping_item, create_user, create_authenticated_client
    ):
        user = create_user()
        shopping_item = create_shopping_item(name="abc", user=user)

        url = reverse(
            "shopping-item-detail",
            kwargs={"pk": shopping_item.shopping_list.pk, "item_pk": shopping_item.pk},
        )
        data = {"name": "updatedName", "purchased": True}
        client = create_authenticated_client(user)
        response = client.put(url, data=data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == data["name"]
        assert response.data["purchased"] == data["purchased"]

    def test_update_shopping_item_invalid_payload_returns_400(
        self, create_shopping_item, create_user, create_authenticated_client
    ):
        user = create_user()
        shopping_item = create_shopping_item(name="abc", user=user)

        url = reverse(
            "shopping-item-detail",
            kwargs={"pk": shopping_item.shopping_list.pk, "item_pk": shopping_item.pk},
        )
        data = {"purchased": True}
        client = create_authenticated_client(user)
        response = client.put(url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_partial_update_shopping_item_returns_200(
        self, create_shopping_item, create_user, create_authenticated_client
    ):
        user = create_user()
        shopping_item = create_shopping_item(name="abc", user=user)

        url = reverse(
            "shopping-item-detail",
            kwargs={"pk": shopping_item.shopping_list.pk, "item_pk": shopping_item.pk},
        )
        data = {"purchased": True}
        client = create_authenticated_client(user)
        response = client.patch(url, data=data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["purchased"] is True

    def test_delete_shopping_item_returns_204(
        self, create_shopping_item, create_user, create_authenticated_client
    ):
        user = create_user()
        shopping_item = create_shopping_item(name="abc", user=user)

        url = reverse(
            "shopping-item-detail",
            kwargs={"pk": shopping_item.shopping_list.pk, "item_pk": shopping_item.pk},
        )
        client = create_authenticated_client(user)
        response = client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
