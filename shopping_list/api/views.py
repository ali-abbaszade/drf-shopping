from rest_framework import generics

from shopping_list.models import ShoppingList, ShoppingItem
from shopping_list.api.serializers import ShoppingListSerializer, ShoppingItemSerializer
from shopping_list.api.permissions import (
    ShoppingListMembersOnly,
    ShoppingItemShoppingListMembersOnly,
    AllShoppingItemsShoppingListMembersOnly,
)


class ListAddShoppingList(generics.ListCreateAPIView):
    serializer_class = ShoppingListSerializer

    def perform_create(self, serializer):
        shopping_list = serializer.save()
        shopping_list.members.add(self.request.user)
        return shopping_list

    def get_queryset(self):
        return ShoppingList.objects.filter(members=self.request.user).order_by(
            "-last_interaction"
        )


class ShoppingListDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer
    permission_classes = [ShoppingListMembersOnly]


class ListAddShoppingItem(generics.ListCreateAPIView):
    serializer_class = ShoppingItemSerializer
    permission_classes = [AllShoppingItemsShoppingListMembersOnly]

    def get_queryset(self):
        shopping_list_id = self.kwargs["pk"]
        queryset = ShoppingItem.objects.filter(shopping_list_id=shopping_list_id)
        return queryset


class ShoppingItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShoppingItem.objects.all()
    serializer_class = ShoppingItemSerializer
    permission_classes = [ShoppingItemShoppingListMembersOnly]
    lookup_url_kwarg = "item_pk"
