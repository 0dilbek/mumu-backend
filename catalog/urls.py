from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BrandViewSet,
    CategoryViewSet,
    FilterMetaViewSet,
    ProductTypeViewSet,
    ProductViewSet,
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('product-types', ProductTypeViewSet, basename='product-type')
router.register('brands', BrandViewSet, basename='brand')
router.register('products', ProductViewSet, basename='product')
router.register('filters', FilterMetaViewSet, basename='filter')

urlpatterns = [
    path('', include(router.urls)),
]
