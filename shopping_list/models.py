from django.db import models

import uuid


class ShoppingItem(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    purchased = models.BooleanField()

    def __str__(self):
        return self.name
