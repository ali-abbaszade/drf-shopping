from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from shopping_list.api import views


urlpatterns = [
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api-token-auth/", obtain_auth_token, name="api-token-auth"),
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
        "api/shopping-lists/<uuid:pk>/add-members/",
        views.ShoppingListAddMembers.as_view(),
        name="shopping-list-add-members",
    ),
    path(
        "api/shopping-lists/<uuid:pk>/remove-members/",
        views.ShoppingListRemoveMembers.as_view(),
        name="shopping-list-remove-members",
    ),
    path(
        "api/shopping-lists/<uuid:pk>/shopping-items/",
        views.ListAddShoppingItem.as_view(),
        name="list-add-shopping-item",
    ),
    path(
        "api/shopping-lists/<uuid:pk>/shopping-items/<uuid:item_pk>/",
        views.ShoppingItemDetail.as_view(),
        name="shopping-item-detail",
    ),
    path(
        "api/search-shopping-items/",
        views.SearchShoppingItems.as_view(),
        name="search_shopping-items",
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
