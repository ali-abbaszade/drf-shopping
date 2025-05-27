from django.contrib.auth import get_user_model
from rest_framework import serializers

from shopping_list.models import ShoppingItem, ShoppingList


User = get_user_model()


class ShoppingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingItem
        fields = ("id", "name", "purchased")

    def create(self, validated_data, **kwargs):
        print(self.context["request"].parser_context)
        validated_data["shopping_list_id"] = self.context["request"].parser_context[
            "kwargs"
        ]["pk"]
        return super(ShoppingItemSerializer, self).create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class ShoppingListSerializer(serializers.ModelSerializer):
    shopping_items = ShoppingItemSerializer(many=True, read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = ShoppingList
        fields = ("id", "name", "shopping_items", "members")
