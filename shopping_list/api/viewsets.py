from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from shopping_list.models import ShoppingItem
from shopping_list.api.serializers import ShoppingItemSerializer


class ShoppingItemViewSet(ModelViewSet):
    queryset = ShoppingItem.objects.all()
    serializer_class = ShoppingItemSerializer

    @action(
        detail=False,
        methods=["delete"],
        url_path="delete-all-purchased",
        url_name="delete-all-purchased",
    )
    def delete_purchased(self, request):
        self.get_queryset().filter(purchased=True).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["patch"])
    def mark_bulk_purchased(self, request):
        try:
            queryset = self.get_queryset().filter(id__in=request.data["shopping_items"])
            updated_count = queryset.update(purchased=True)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response({"updated": updated_count}, status=status.HTTP_200_OK)
