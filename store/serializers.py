from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Product, Cart, CartItem, ProductImage
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'thumbnail', 'uploaded_at')
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'category', 'category_id', 'stock', 'images', 'created_at', 'updated_at')
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    class Meta:
        model = CartItem
        fields = ('id', 'cart', 'product', 'product_id', 'quantity')
        read_only_fields = ('cart',)
class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ('id', 'user', 'created_at', 'updated_at', 'items')
User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
