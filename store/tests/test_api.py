import io
import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from store.models import Category, Product

BASE_URL = "/api/products/"   

@pytest.mark.django_db
def test_get_products():
    client = APIClient()
    response = client.get(BASE_URL)

    assert response.status_code == 200


@pytest.mark.django_db
def test_pagination():
    client = APIClient()
    category = Category.objects.create(name="Cat A")
    Product.objects.bulk_create([
        Product(name=f"Product {i}", price=100, category=category)
        for i in range(15)
    ])

    response = client.get(BASE_URL)

    assert response.status_code == 200
    assert "results" in response.data
    assert len(response.data["results"]) == 10


from unittest.mock import patch

@pytest.mark.django_db
@patch("store.views.external_api_call")
def test_mock_external_api(mock_api):
    mock_api.return_value = {"status": "mocked"}

    client = APIClient()
    response = client.get("/api/external/")

    assert response.status_code == 200
    assert response.data["status"] == "mocked"

@pytest.mark.django_db
def test_external_api_real():
    client = APIClient()

    response = client.get("/api/external/")

    assert response.status_code == 200
    assert response.data["status"] == "real response"

@pytest.mark.django_db
def test_create_product():
    client = APIClient()
    category = Category.objects.create(name="Cat B")

    response = client.post("/api/products/", {
        "name": "Test",
        "price": "100.00",
        "category_id": category.id
    }, format="json")

    assert response.status_code == 201
    assert response.data["name"] == "Test"


def _make_test_image_bytes():
    from PIL import Image
    img = Image.new("RGB", (300, 300), color=(0, 255, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.mark.django_db
def test_upload_images_creates_thumbnail(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    client = APIClient()

    category = Category.objects.create(name="Img Cat")
    product = Product.objects.create(name="Img Product", price=10, category=category)

    img_bytes = _make_test_image_bytes()
    upload = SimpleUploadedFile("img.jpg", img_bytes, content_type="image/jpeg")

    response = client.post(f"/api/products/{product.id}/upload_images/", {"images": [upload]}, format="multipart")

    assert response.status_code == 201
    assert isinstance(response.data, list)
    assert response.data[0]["thumbnail"] is not None


@pytest.mark.django_db
def test_cart_requires_auth():
    client = APIClient()
    response = client.get("/api/carts/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_cart_item_flow_authenticated():
    client = APIClient()
    user = get_user_model().objects.create_user(username="buyer", password="pass")
    client.force_authenticate(user=user)

    category = Category.objects.create(name="Cart Cat")
    product = Product.objects.create(name="Cart Product", price=5, category=category)

    response = client.post("/api/cart-items/", {"product_id": product.id, "quantity": 2}, format="json")
    assert response.status_code == 201

    list_response = client.get("/api/cart-items/")
    assert list_response.status_code == 200
    assert len(list_response.data["results"]) == 1
