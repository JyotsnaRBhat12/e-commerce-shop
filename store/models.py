import os
import magic
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.db import models
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal

def validate_image_file(value):
    # Read the first 2048 bytes of the file for magic numbers
    file_bytes = value.read(2048)
    # Important: Reset file pointer to the beginning after reading!
    value.seek(0)
    
    mime_type = magic.from_buffer(file_bytes, mime=True)
    valid_mime_types = ['image/jpeg', 'image/png']
    
    if mime_type not in valid_mime_types:
        raise ValidationError(f'Unsupported file type: {mime_type}. Allowed types are JPEG and PNG.')
    
    filesize = value.size
    if filesize > 2 * 1024 * 1024:
        raise ValidationError("The maximum file size that can be uploaded is 2MB")
    else:
        return value


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='carts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart({self.user.username})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user.username}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/', validators=[validate_image_file])
    thumbnail = models.ImageField(upload_to='product_thumbnails/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Prevent recreating thumbnail if one already exists or self.image is empty
        if self.image and not self.thumbnail:
            img = Image.open(self.image)
            # Create a 200x200 thumbnail
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            
            thumb_io = BytesIO()
            format = 'JPEG' if self.image.name.lower().endswith(('.jpg', '.jpeg')) else 'PNG'
            img.save(thumb_io, format=format)
            
            thumb_name = f"thumb_{os.path.basename(self.image.name)}"
            self.thumbnail.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.name}"