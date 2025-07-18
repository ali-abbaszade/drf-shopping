from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from shopping_list.models import ShoppingList, ShoppingItem
from shopping_list.api.serializers import (
    ShoppingListSerializer,
    ShoppingItemSerializer,
    AddMemberSerializer,
    RemoveMemberSerializer,
)
from shopping_list.api.permissions import (
    ShoppingListMembersOnly,
    ShoppingItemShoppingListMembersOnly,
    AllShoppingItemsShoppingListMembersOnly,
)
from shopping_list.api.pagination import LargerResultsSetPagination


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
    pagination_class = LargerResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["name", "purchased"]

    def get_queryset(self):
        shopping_list_id = self.kwargs["pk"]
        queryset = ShoppingItem.objects.filter(
            shopping_list_id=shopping_list_id
        ).order_by("purchased")

        return queryset


class ShoppingItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShoppingItem.objects.all()
    serializer_class = ShoppingItemSerializer
    permission_classes = [ShoppingItemShoppingListMembersOnly]
    lookup_url_kwarg = "item_pk"


class ShoppingListAddMembers(APIView):
    permission_classes = [ShoppingListMembersOnly]

    @extend_schema(request=AddMemberSerializer, responses=AddMemberSerializer)
    def put(self, request, pk, format=None):
        shopping_list = ShoppingList.objects.get(pk=pk)
        serializer = AddMemberSerializer(shopping_list, data=request.data)
        self.check_object_permissions(request, shopping_list)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ShoppingListRemoveMembers(APIView):
    permission_classes = [ShoppingListMembersOnly]

    @extend_schema(request=RemoveMemberSerializer, responses=RemoveMemberSerializer)
    def put(self, request, pk, format=None):
        shopping_list = ShoppingList.objects.get(pk=pk)
        serializer = RemoveMemberSerializer(shopping_list, data=request.data)
        self.check_object_permissions(request, shopping_list)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SearchShoppingItems(generics.ListAPIView):
    serializer_class = ShoppingItemSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        users_shopping_lists = ShoppingList.objects.filter(members=self.request.user)
        queryset = ShoppingItem.objects.filter(shopping_list__in=users_shopping_lists)

        return queryset
