import io
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from store.models import Product, Category, ProductImage, Cart, CartItem, validate_image_file
def _make_test_image_bytes():
    from PIL import Image
    img = Image.new("RGB", (300, 300), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()
@pytest.mark.django_db
def test_product_creation():
    category = Category.objects.create(name="Test Category")
    product = Product.objects.create(
        name="Test Product",
        price=100,
        category=category
    )
    assert product.name == "Test Product"
def test_validate_image_file_rejects_extension():
    bad_file = SimpleUploadedFile("file.txt", b"not an image")
    with pytest.raises(ValidationError):
        validate_image_file(bad_file)
def test_validate_image_file_rejects_large_file():
    big_content = b"a" * (2 * 1024 * 1024 + 1)
    big_file = SimpleUploadedFile("big.jpg", big_content, content_type="image/jpeg")
    with pytest.raises(ValidationError):
        validate_image_file(big_file)
@pytest.mark.django_db
def test_product_image_thumbnail_created(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    category = Category.objects.create(name="Img Category")
    product = Product.objects.create(name="Img Product", price=10, category=category)
    img_bytes = _make_test_image_bytes()
    upload = SimpleUploadedFile("test.jpg", img_bytes, content_type="image/jpeg")
    prod_img = ProductImage(product=product, image=upload)
    prod_img.full_clean()
    prod_img.save()
    assert prod_img.thumbnail.name != ""
    assert prod_img.thumbnail.storage.exists(prod_img.thumbnail.name)
@pytest.mark.django_db
def test_cart_item_unique_together():
    category = Category.objects.create(name="Cart Category")
    product = Product.objects.create(name="Cart Product", price=5, category=category)
    from django.contrib.auth import get_user_model
    user = get_user_model().objects.create_user(username="u1", password="pass")
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=1)
    with pytest.raises(IntegrityError):
        CartItem.objects.create(cart=cart, product=product, quantity=2)
