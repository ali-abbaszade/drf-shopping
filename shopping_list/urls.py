from django.urls import path, include


from shopping_list.api import views


urlpatterns = [
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path(
        "api/shopping-lists/",
        views.ListAddShoppingList.as_view(),
        name="all-shopping-lists",
    ),
    path(
        "api/shopping-lists/<uuid:pk>/",
        views.ShoppingListDetail.as_view(),
        name="shopping-list-detail",
    ),
    path(
        "api/shopping-lists/<uuid:pk>/shopping-items/",
        views.AddShoppingItem.as_view(),
        name="add-shopping-item",
    ),
    path(
        "api/shopping-lists/<uuid:pk>/shopping-items/<uuid:item_pk>/",
        views.ShoppingItemDetail.as_view(),
        name="shopping-item-detail",
    ),
]
