from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewset import SaleViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'sales', SaleViewSet, basename='sale')

urlpatterns = router.urls