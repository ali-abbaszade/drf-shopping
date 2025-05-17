from django.urls import path, include
from rest_framework.routers import DefaultRouter

from shopping_list.api import viewsets

router = DefaultRouter()
router.register("shopping-items", viewsets.ShoppingItemViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
