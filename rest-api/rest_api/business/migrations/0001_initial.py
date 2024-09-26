# Generated by Django 5.1.1 on 2024-09-26 19:45

import django.core.validators
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField(blank=True, null=True)),
                ('modification_type', models.CharField(blank=True, choices=[('insert', 'insert'), ('update', 'update'), ('delete', 'delete')], max_length=6, null=True)),
                ('employee_id', models.IntegerField()),
                ('first_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(max_length=100)),
                ('pesel', models.CharField(blank=True, max_length=11, null=True)),
                ('date_of_birth', models.DateField()),
                ('identity_document', models.CharField(choices=[('passport', 'Passport'), ('id_card', 'Identity Card')], max_length=8)),
                ('identity_document_number', models.CharField(max_length=15)),
                ('phone_country_code', models.CharField(max_length=3, validators=[django.core.validators.RegexValidator(message='Country code must start with "+" followed by 2 digits.', regex='^\\+[0-9]{2}$')])),
                ('phone_number', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message='Phone number must contain only digits.', regex='^\\d+$')])),
                ('email', models.EmailField(max_length=254, validators=[django.core.validators.EmailValidator(message='Enter a valid email address.')])),
                ('street', models.CharField(blank=True, max_length=50, null=True)),
                ('house_number', models.CharField(max_length=5)),
                ('apartment_number', models.CharField(blank=True, max_length=5, null=True)),
                ('postal_code', models.CharField(max_length=6, validators=[django.core.validators.RegexValidator(message='Postal code must be in the format xx-xxx.', regex='^\\d{2}-\\d{3}$')])),
                ('city', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
                ('bank_country_code', models.CharField(max_length=2)),
                ('bank_account_number', models.CharField(max_length=26, validators=[django.core.validators.RegexValidator(message='Bank account number must be exactly 26 digits.', regex='^\\d{26}$')])),
                ('bank_name', models.CharField(max_length=100)),
                ('bank_swift', models.CharField(max_length=11)),
                ('date_of_employment', models.DateField()),
                ('position', models.CharField(max_length=100)),
                ('department', models.CharField(max_length=100)),
                ('salary', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField(blank=True, null=True)),
                ('modification_type', models.CharField(blank=True, choices=[('insert', 'insert'), ('update', 'update'), ('delete', 'delete')], max_length=6, null=True)),
                ('item_id', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
                ('index', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'), message='Price must be greater than zero.')])),
                ('cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'), message='Cost must be greater than zero.')])),
                ('sku', models.CharField(max_length=100, validators=[django.core.validators.RegexValidator(message='SKU must contain only alphanumeric characters, underscores, or hyphens.', regex='^[A-Za-z0-9_-]+$')])),
                ('barcode', models.CharField(blank=True, max_length=100, null=True, validators=[django.core.validators.RegexValidator(message='Barcode must be between 8 and 13 digits.', regex='^\\d{8,13}$')])),
                ('ean', models.CharField(blank=True, max_length=13, null=True, validators=[django.core.validators.RegexValidator(message='EAN must be exactly 13 digits.', regex='^\\d{13}$')])),
                ('upc', models.CharField(blank=True, max_length=12, null=True, validators=[django.core.validators.RegexValidator(message='UPC must be exactly 12 digits.', regex='^\\d{12}$')])),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'), message='Weight must be greater than zero.')])),
                ('dimensions', models.CharField(blank=True, max_length=100, null=True, validators=[django.core.validators.RegexValidator(message='Dimensions must be in the format LxWxH.', regex='^\\d+(\\.\\d+)?x\\d+(\\.\\d+)?x\\d+(\\.\\d+)?$')])),
                ('volume', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'), message='Volume must be greater than zero.')])),
                ('stock_quantity', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0, message='Stock Quantity cannot be negative.')])),
                ('reorder_level', models.IntegerField(default=10, validators=[django.core.validators.MinValueValidator(0, message='Reorder Level cannot be negative.')])),
                ('warehouse_location', models.CharField(blank=True, max_length=255, null=True)),
                ('supplier_sku', models.CharField(blank=True, max_length=100, null=True)),
                ('lead_time', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0, message='Lead Time must be non-negative.')])),
                ('vat_rate', models.DecimalField(decimal_places=2, default=23.0, max_digits=4, validators=[django.core.validators.MinValueValidator(Decimal('0.00'), message='VAT Rate cannot be negative.')])),
                ('tax_category', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
