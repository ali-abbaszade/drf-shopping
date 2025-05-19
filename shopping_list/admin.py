from django.contrib import admin

from shopping_list.models import ShoppingItem, ShoppingList


@admin.register(ShoppingItem)
class ShoppingItemAdmin(admin.ModelAdmin):
    list_display = ["name", "purchased", "shopping_list"]


class ShoppingItemInline(admin.StackedInline):
    model = ShoppingItem


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    inlines = [ShoppingItemInline]
