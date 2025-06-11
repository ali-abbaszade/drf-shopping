from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from shopping_list.models import ShoppingItem, ShoppingList, User


@admin.register(ShoppingItem)
class ShoppingItemAdmin(admin.ModelAdmin):
    list_display = ["name", "purchased", "shopping_list"]


class ShoppingItemInline(admin.StackedInline):
    model = ShoppingItem


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    inlines = [ShoppingItemInline]


admin.site.register(User, UserAdmin)
