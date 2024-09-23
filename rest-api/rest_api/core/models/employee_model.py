from django.core.validators import EmailValidator, RegexValidator
from django.db import models

from .base_model import BaseModel
from ..managers.user_manager import UserManager


class Employee(BaseModel):
    objects = UserManager()

    class IdentityDocuments(models.TextChoices):
        PASSPORT = 'passport', 'Passport'
        ID_CARD = 'id_card', 'Identity Card'

    employee_id = models.IntegerField(verbose_name="Employee ID")

    first_name = models.CharField(max_length=50, verbose_name="First Name")
    middle_name = models.CharField(max_length=50, null=True, blank=True, verbose_name="Middle Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    pesel = models.CharField(max_length=11, null=True, blank=True, verbose_name="PESEL")
    date_of_birth = models.DateField(verbose_name="Date of Birth")

    identity_document = models.CharField(max_length=8, choices=IdentityDocuments.choices,
                                         verbose_name="Identity Document Type")
    identity_document_number = models.CharField(max_length=15, verbose_name="Identity Document Number")

    phone_country_code = models.CharField(max_length=3, verbose_name="Phone Country Code", validators=[
        RegexValidator(regex=r'^\+[0-9]{2}$', message='Country code must start with "+" followed by 2 digits.')])
    phone_number = models.CharField(max_length=15, verbose_name="Phone Number", validators=[
        RegexValidator(regex=r'^\d+$', message='Phone number must contain only digits.')])
    email = models.EmailField(verbose_name="Email Address",
                              validators=[EmailValidator(message="Enter a valid email address.")])

    street = models.CharField(max_length=50, null=True, blank=True, verbose_name="Street")
    house_number = models.CharField(max_length=5, verbose_name="House Number")
    apartment_number = models.CharField(max_length=5, null=True, blank=True, verbose_name="Apartment Number")
    postal_code = models.CharField(max_length=6, verbose_name="Postal Code", validators=[
        RegexValidator(regex=r'^\d{2}-\d{3}$', message='Postal code must be in the format xx-xxx.')])
    city = models.CharField(max_length=50, verbose_name="City")
    country = models.CharField(max_length=50, verbose_name="Country")

    bank_country_code = models.CharField(max_length=2, verbose_name="Bank Country Code")
    bank_account_number = models.CharField(max_length=26, verbose_name="Bank Account Number", validators=[
        RegexValidator(regex=r'^\d{26}$', message='Bank account number must be exactly 26 digits.')])
    bank_name = models.CharField(max_length=100, verbose_name="Bank Name")
    bank_swift = models.CharField(max_length=11, verbose_name="Bank SWIFT Code")

    date_of_employment = models.DateField(verbose_name="Date of Employment")
    position = models.CharField(max_length=100, verbose_name="Position")
    department = models.CharField(max_length=100, verbose_name="Department")
    salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salary")

    def __str__(self):
        if not self.middle_name:
            return f'{self.first_name} {self.last_name}'
        return f'{self.first_name} {self.middle_name} {self.last_name}'
