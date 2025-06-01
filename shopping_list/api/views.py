from rest_framework import generics

from shopping_list.models import ShoppingList, ShoppingItem
from shopping_list.api.serializers import ShoppingListSerializer, ShoppingItemSerializer

from shopping_list.api.permissions import (
    ShoppingListMembersOnly,
    ShoppingItemShoppingListMembersOnly,
    AllShoppingItemsShoppingListMembersOnly,
)


class ListAddShoppingList(generics.ListCreateAPIView):
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer

    def perform_create(self, serializer):
        shopping_list = serializer.save()
        shopping_list.members.add(self.request.user)
        return shopping_list


class ShoppingListDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer
    permission_classes = [ShoppingListMembersOnly]


class AddShoppingItem(generics.CreateAPIView):
    queryset = ShoppingItem.objects.all()
    serializer_class = ShoppingItemSerializer
    permission_classes = [AllShoppingItemsShoppingListMembersOnly]


class ShoppingItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShoppingItem.objects.all()
    serializer_class = ShoppingItemSerializer
    permission_classes = [ShoppingItemShoppingListMembersOnly]
    lookup_url_kwarg = "item_pk"
