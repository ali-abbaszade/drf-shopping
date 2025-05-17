from django.contrib import admin

from shopping_list.models import ShoppingItem


@admin.register(ShoppingItem)
class ShoppingItemAdmin(admin.ModelAdmin):
    pass
