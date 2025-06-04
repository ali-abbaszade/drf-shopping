from django.db import models

import uuid


class ShoppingList(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    members = models.ManyToManyField("auth.User")
    last_interaction = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ShoppingItem(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    purchased = models.BooleanField()
    shopping_list = models.ForeignKey(
        ShoppingList, on_delete=models.CASCADE, related_name="shopping_items"
    )

    def __str__(self):
        return self.name
