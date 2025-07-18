from typing import List, TypedDict
from django.contrib.auth import get_user_model
from rest_framework import serializers

from shopping_list.models import ShoppingItem, ShoppingList


User = get_user_model()


class ShoppingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingItem
        fields = ("id", "name", "purchased")

    def create(self, validated_data, **kwargs):
        validated_data["shopping_list_id"] = self.context["request"].parser_context[
            "kwargs"
        ]["pk"]

        if ShoppingList.objects.get(
            id=validated_data["shopping_list_id"]
        ).shopping_items.filter(name=validated_data["name"], purchased=False):
            raise serializers.ValidationError("There is already this item on the list")

        return super(ShoppingItemSerializer, self).create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class UnpurchasedItem(TypedDict):
    name: str


class ShoppingListSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    unpurchased_items = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingList
        fields = ("id", "name", "unpurchased_items", "members")

    def get_unpurchased_items(self, obj) -> List[UnpurchasedItem]:
        return [
            {"name": shopping_item.name}
            for shopping_item in obj.shopping_items.filter(purchased=False)[:3]
        ]


class AddMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ["members"]

    def update(self, instance, validated_data):
        for member in validated_data["members"]:
            instance.members.add(member)
            instance.save()

        return instance


class RemoveMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ["members"]

    def update(self, instance, validated_data):
        for member in validated_data["members"]:
            instance.members.remove(member)
            instance.save()

        return instance
