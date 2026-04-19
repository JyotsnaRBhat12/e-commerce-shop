from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ExternalAPIView
from .views import CategoryViewSet, ProductViewSet, CartViewSet, CartItemViewSet, UserListView
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cartitem')
urlpatterns = [
    path('auth/users/', UserListView.as_view(), name='user-list'),
    path('', include(router.urls)),
]
urlpatterns += [
    path('external/', ExternalAPIView.as_view()),
]
