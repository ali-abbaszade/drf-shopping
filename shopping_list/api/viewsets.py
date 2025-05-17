from rest_framework.viewsets import ModelViewSet

from shopping_list.models import ShoppingItem
from shopping_list.api.serializers import ShoppingItemSerializer


class ShoppingItemViewSet(ModelViewSet):
    queryset = ShoppingItem.objects.all()
    serializer_class = ShoppingItemSerializer
