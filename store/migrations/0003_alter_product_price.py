import django.core.validators
from decimal import Decimal
from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [
        ('store', '0002_productimage'),
    ]
    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
    ]
