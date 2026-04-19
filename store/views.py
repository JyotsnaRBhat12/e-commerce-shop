from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from rest_framework.views import APIView

from .models import Category, Product, Cart, CartItem, ProductImage
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    CartSerializer,
    CartItemSerializer,
    UserSerializer,
    ProductImageSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = {
        'price': ['exact', 'lt', 'lte', 'gt', 'gte'],
        'category__id': ['exact'],
    }
    search_fields = ('name', 'description')
    ordering_fields = ('price', 'name', 'created_at')

    @action(detail=True, methods=['post'])
    def upload_images(self, request, pk=None):
        product = self.get_object()
        images = request.FILES.getlist('images')

        if not images:
            return Response(
                {'error': 'No images provided. Please upload files using the key "images".'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        created_images = []
        failed_images = []
        
        for image_file in images:
            prod_img = ProductImage(product=product, image=image_file)
            try:
                prod_img.full_clean()
                prod_img.save()
                created_images.append(prod_img)
            except ValidationError as e:
                # e.message_dict contains field level errors as a dictionary
                try:
                    error_msg = e.message_dict
                except AttributeError:
                    error_msg = list(e.messages)

                failed_images.append({
                    'filename': image_file.name,
                    'errors': error_msg
                })

        serializer = ProductImageSerializer(created_images, many=True)
        
        response_data = {
            'successful': serializer.data,
            'failed': failed_images
        }
        
        # If any failed, return a 207 Multi-Status equivalent response (using 200 OK since DRF doesn't natively expose 207 constant easily without custom status). 
        # But we can just return HTTP 207 as integer or 200. We will use 200 OK as it has varying statuses inside.
        response_status = status.HTTP_200_OK if failed_images else status.HTTP_201_CREATED
        
        if failed_images and not created_images:
            response_status = status.HTTP_400_BAD_REQUEST
            
        return Response(response_data, status=response_status)


class CartViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)


class UserListView(generics.ListAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer




def external_api_call():
    return {"status": "real response"}



class ExternalAPIView(APIView):
    def get(self, request):
        data = external_api_call()
        return Response(data)