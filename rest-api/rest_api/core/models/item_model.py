from decimal import Decimal

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from .base_model import BaseModel
from ..managers.item_manager import ItemManager


class Item(BaseModel):
    objects = ItemManager()

    item_id = models.IntegerField(verbose_name="Item ID")

    name = models.CharField(max_length=255, verbose_name="Name")
    index = models.CharField(max_length=50, verbose_name="Index")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    # category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, verbose_name="Category")

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price",
                                validators=[
                                    MinValueValidator(Decimal('0.01'), message="Price must be greater than zero.")])
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Cost Price",
                               validators=[
                                   MinValueValidator(Decimal('0.01'), message="Cost must be greater than zero.")])
    # discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
    #                                      verbose_name="Discount Price", validators=[
    #         MinValueValidator(0.00, message="Discount Price cannot be negative.")])

    sku = models.CharField(max_length=100, verbose_name="SKU", validators=[
        RegexValidator(regex=r'^[A-Za-z0-9_-]+$',
                       message='SKU must contain only alphanumeric characters, underscores, or hyphens.')])
    barcode = models.CharField(max_length=100, blank=True, null=True, verbose_name="Barcode", validators=[
        RegexValidator(regex=r'^\d{8,13}$', message='Barcode must be between 8 and 13 digits.')])
    ean = models.CharField(max_length=13, blank=True, null=True, verbose_name="EAN",
                           validators=[RegexValidator(regex=r'^\d{13}$', message='EAN must be exactly 13 digits.')])
    upc = models.CharField(max_length=12, blank=True, null=True, verbose_name="UPC",
                           validators=[RegexValidator(regex=r'^\d{12}$', message='UPC must be exactly 12 digits.')])

    weight = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, verbose_name="Weight (kg)",
                                 validators=[
                                     MinValueValidator(Decimal('0.01'), message="Weight must be greater than zero.")])
    dimensions = models.CharField(max_length=100, blank=True, null=True, verbose_name="Dimensions (LxWxH)", validators=[
        RegexValidator(regex=r'^\d+(\.\d+)?x\d+(\.\d+)?x\d+(\.\d+)?$',
                       message='Dimensions must be in the format LxWxH.')])
    volume = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True, verbose_name="Volume (m³)",
                                 validators=[
                                     MinValueValidator(Decimal('0.01'), message="Volume must be greater than zero.")])
    stock_quantity = models.IntegerField(default=0, verbose_name="Stock Quantity", validators=[
        MinValueValidator(0, message="Stock Quantity cannot be negative.")])
    reorder_level = models.IntegerField(default=10, verbose_name="Reorder Level",
                                        validators=[MinValueValidator(0, message="Reorder Level cannot be negative.")])

    warehouse_location = models.CharField(max_length=255, blank=True, null=True, verbose_name="Warehouse Location")

    # supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Supplier")
    supplier_sku = models.CharField(max_length=100, blank=True, null=True, verbose_name="Supplier SKU")
    lead_time = models.IntegerField(blank=True, null=True, verbose_name="Lead Time (days)",
                                    validators=[MinValueValidator(0, message="Lead Time must be non-negative.")])

    vat_rate = models.DecimalField(max_digits=4, decimal_places=2, default=23.00, verbose_name="VAT Rate (%)",
                                   validators=[
                                       MinValueValidator(Decimal('0.00'), message="VAT Rate cannot be negative.")])
    tax_category = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tax Category")

    # image = models.ImageField(upload_to='items/images/', blank=True, null=True, verbose_name="Item Image")
    # datasheet = models.FileField(upload_to='items/datasheets/', blank=True, null=True, verbose_name="Datasheet")
    #
    # attributes = models.JSONField(default=dict, blank=True, null=True, verbose_name="Custom Attributes")

    def __str__(self):
        return self.name
