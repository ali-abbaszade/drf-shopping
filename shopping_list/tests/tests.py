from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

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
        client = create_authenticated_client(user)
        create_shopping_list(name="abc", user=user)

        another_user = User.objects.create_user(
            "another", "another@user.com", "something"
        )
        create_shopping_list(name="xyz", user=another_user)

        url = reverse("all-shopping-lists")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "abc"

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
        assert len(response.data["unpurchased_items"]) == 1
        assert response.data["unpurchased_items"][0]["name"] == "a"

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

    def test_update_shopping_list_non_member_restricted_returns_403(
        self, create_shopping_list, create_user, create_authenticated_client
    ):
        creator_user = create_user()
        shopping_list = create_shopping_list(name="a", user=creator_user)
        another_user = User.objects.create_user(
            "another_user", "another@user.com", "something"
        )
        client = create_authenticated_client(another_user)

        url = reverse("shopping-list-detail", args=[shopping_list.pk])
        data = {
            "name": "xyz",
        }

        response = client.put(url, data=data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_partial_update_shopping_list_non_member_restricted_returns_403(
        self, create_shopping_list, create_user, create_authenticated_client
    ):
        creator_user = create_user()
        shopping_list = create_shopping_list(name="a", user=creator_user)
        another_user = User.objects.create_user(
            "another_user", "another@user.com", "something"
        )
        client = create_authenticated_client(another_user)

        url = reverse("shopping-list-detail", args=[shopping_list.pk])
        data = {
            "name": "xyz",
        }

        response = client.patch(url, data=data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_shopping_list_non_member_restricted_returns_403(
        self, create_shopping_list, create_user, create_authenticated_client
    ):
        creator_user = create_user()
        shopping_list = create_shopping_list(name="a", user=creator_user)
        another_user = User.objects.create_user(
            "another", "another@email.com", "something"
        )
        client = create_authenticated_client(another_user)

        url = reverse("shopping-list-detail", args=[shopping_list.pk])
        response = client.delete(url, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_user_should_retrieve_shopping_list_returns_200(
        self, create_shopping_list, create_user, admin_client
    ):
        user = create_user()
        shopping_list = create_shopping_list(name="a", user=user)

        url = reverse("shopping-list-detail", args=[shopping_list.pk])
        response = admin_client.get(url, format="json")

        assert response.status_code == status.HTTP_200_OK

    def test_max_3_shopping_item_on_shopping_list_returns_200(
        self, create_user, create_authenticated_client, create_shopping_list
    ):
        user = create_user()
        shopping_list = create_shopping_list("abc", user)

        ShoppingItem.objects.create(
            name="item-1", purchased=False, shopping_list=shopping_list
        )
        ShoppingItem.objects.create(
            name="item-2", purchased=False, shopping_list=shopping_list
        )
        ShoppingItem.objects.create(
            name="item-3", purchased=False, shopping_list=shopping_list
        )
        ShoppingItem.objects.create(
            name="item-4", purchased=False, shopping_list=shopping_list
        )

        client = create_authenticated_client(user)
        url = reverse("shopping-list-detail", args=[shopping_list.pk])
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["unpurchased_items"]) == 3

    def test_all_shopping_items_on_shopping_list_unpurchased_returns_200(
        self, create_user, create_authenticated_client, create_shopping_list
    ):
        user = create_user()
        shopping_list = create_shopping_list("abc", user)

        ShoppingItem.objects.create(
            name="a", shopping_list=shopping_list, purchased=False
        )
        ShoppingItem.objects.create(
            name="b", shopping_list=shopping_list, purchased=False
        )
        ShoppingItem.objects.create(
            name="c", shopping_list=shopping_list, purchased=True
        )

        client = create_authenticated_client(user)
        url = reverse("shopping-list-detail", args=[shopping_list.pk])
        response = client.get(url)

        response.status_code == status.HTTP_200_OK
        assert len(response.data["unpurchased_items"]) == 2


@pytest.mark.django_db
class TestShoppingItem:
    def test_shopping_item_valid_payload_create_returns_201(
        self, create_user, create_shopping_list, create_authenticated_client
    ):
        user = create_user()
        shopping_list = create_shopping_list(name="a", user=user)

        url = reverse("list-add-shopping-item", args=[shopping_list.pk])
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

        url = reverse("list-add-shopping-item", args=[shopping_list.pk])
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

    def test_non_member_of_list_should_not_add_shopping_item_returns_403(
        self, create_user, create_shopping_list, create_authenticated_client
    ):
        creator_user = create_user()
        shopping_list = create_shopping_list(name="abc", user=creator_user)

        another_user = User.objects.create_user(
            "another", "another@email.com", "something"
        )
        client = create_authenticated_client(another_user)

        url = reverse("list-add-shopping-item", args=[shopping_list.pk])
        data = {
            "name": "new item",
            "purchased": False,
        }
        response = client.post(url, data=data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_user_can_add_shopping_item_returns_201(
        self, create_shopping_list, create_user, admin_client
    ):
        user = create_user()
        shopping_list = create_shopping_list(user=user, name="a")

        url = reverse("list-add-shopping-item", args=[shopping_list.pk])
        data = {
            "name": "new item",
            "purchased": False,
        }
        response = admin_client.post(url, data=data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

    def test_shopping_item_detail_access_restricted_for_non_member_returns_403(
        self, create_shopping_item, create_user, create_authenticated_client
    ):
        creator_user = create_user()
        shopping_item = create_shopping_item(user=creator_user, name="abc")
        another_user = User.objects.create_user(
            "another", "another@user.com", "something"
        )
        client = create_authenticated_client(another_user)

        url = reverse(
            "shopping-item-detail",
            kwargs={"pk": shopping_item.shopping_list.pk, "item_pk": shopping_item.pk},
        )
        response = client.get(url, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_shopping_item_detail_update_restricted_for_non_member_returns_403(
        self, create_shopping_item, create_user, create_authenticated_client
    ):
        creator_user = create_user()
        shopping_item = create_shopping_item(user=creator_user, name="abc")
        another_user = User.objects.create_user(
            "another", "another@user.com", "something"
        )
        client = create_authenticated_client(another_user)

        url = reverse(
            "shopping-item-detail",
            kwargs={"pk": shopping_item.shopping_list.pk, "item_pk": shopping_item.pk},
        )
        data = {
            "name": "new name",
            "purchased": False,
        }
        response = client.put(url, data=data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_shopping_item_detail_partial_update_restricted_for_non_member_returns_403(
        self, create_shopping_item, create_user, create_authenticated_client
    ):
        creator_user = create_user()
        shopping_item = create_shopping_item(user=creator_user, name="abc")
        another_user = User.objects.create_user(
            "another", "another@user.com", "something"
        )
        client = create_authenticated_client(another_user)

        url = reverse(
            "shopping-item-detail",
            kwargs={"pk": shopping_item.shopping_list.pk, "item_pk": shopping_item.pk},
        )
        data = {
            "purchased": True,
        }
        response = client.patch(url, data=data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_shopping_item_delete_restricted_for_non_member_return_403(
        self, create_user, create_shopping_item, create_authenticated_client
    ):
        creator_user = create_user()
        shopping_item = create_shopping_item(name="abc", user=creator_user)
        another_user = User.objects.create_user(
            "another", "another@user.com", "something"
        )
        client = create_authenticated_client(another_user)

        url = reverse(
            "shopping-item-detail",
            kwargs={"pk": shopping_item.shopping_list.pk, "item_pk": shopping_item.pk},
        )
        response = client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_user_should_retrieve_single_shopping_item_returns_200(
        self, create_user, create_shopping_item, admin_client
    ):
        user = create_user()
        shopping_item = create_shopping_item(name="xyz", user=user)

        url = reverse(
            "shopping-item-detail",
            kwargs={"pk": shopping_item.shopping_list.pk, "item_pk": shopping_item.pk},
        )
        response = admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_list_shopping_item_retrieved_by_shopping_list_member_returns_200(
        self, create_user, create_authenticated_client, create_shopping_list
    ):
        user = create_user()
        shopping_list = create_shopping_list(name="abc", user=user)
        shopping_item_1 = ShoppingItem.objects.create(
            name="a", purchased=False, shopping_list=shopping_list
        )
        shopping_item_2 = ShoppingItem.objects.create(
            name="b", purchased=False, shopping_list=shopping_list
        )

        client = create_authenticated_client(user)
        url = reverse("list-add-shopping-item", args=[shopping_list.pk])
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert response.data[0]["name"] == shopping_item_1.name
        assert response.data[1]["name"] == shopping_item_2.name

    def test_non_member_can_not_access_shopping_item_returns_403(
        self, create_user, create_authenticated_client, create_shopping_item
    ):
        creator_user = create_user()
        shopping_item = create_shopping_item(name="abc", user=creator_user)

        another_user = User.objects.create_user(
            "another", "another@user.com", "something"
        )
        client = create_authenticated_client(another_user)
        url = reverse("list-add-shopping-item", args=[shopping_item.shopping_list.pk])
        response = client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_return_shopping_item_the_ones_belonging_to_particular_list_return_200(
        self, create_user, create_authenticated_client, create_shopping_list
    ):
        user = create_user()
        shopping_list = create_shopping_list("abc", user)
        shopping_item_form_this_list = ShoppingItem.objects.create(
            name="a", purchased=False, shopping_list=shopping_list
        )

        another_shopping_list = create_shopping_list("another list", user)
        ShoppingItem.objects.create(
            name="b", purchased=False, shopping_list=another_shopping_list
        )

        client = create_authenticated_client(user)
        url = reverse("list-add-shopping-item", args=[shopping_list.pk])
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == shopping_item_form_this_list.name

    def test_duplicate_item_on_list_returns_400(
        self, create_user, create_authenticated_client, create_shopping_list
    ):
        user = create_user()
        shopping_list = create_shopping_list("abc", user)
        ShoppingItem.objects.create(
            name="a", purchased=False, shopping_list=shopping_list
        )

        client = create_authenticated_client(user)
        url = reverse("list-add-shopping-item", args=[shopping_list.pk])
        data = {
            "name": "a",
            "purchased": False,
        }
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
