from django.core.validators import EmailValidator, RegexValidator
from django.db import models

from ..managers.user_manager import UserManager
from .base_model import BaseModel


class Employee(BaseModel):
    objects = UserManager()

    class IdentityDocuments(models.TextChoices):
        PASSPORT = 'passport', 'Passport'
        ID_CARD = 'id_card', 'Identity Card'

    employee_id = models.IntegerField()

    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=100)
    identity_document = models.CharField(max_length=8, choices=IdentityDocuments.choices)
    identity_document_number = models.CharField(max_length=15)
    pesel = models.CharField(max_length=11, null=True, blank=True)
    date_of_birth = models.DateField()

    phone_country_code = models.CharField(
        max_length=3,
        validators=[
            RegexValidator(regex=r'^\+[0-9]{2}$', message='Country code must start with "+" followed by 2 digits.')]
    )
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\d+$', message='Phone number must contain only digits.')]
    )
    email = models.EmailField(validators=[EmailValidator(message="Enter a valid email address.")])

    street = models.CharField(max_length=50, null=True, blank=True)
    house_number = models.CharField(max_length=5)
    apartment_number = models.CharField(max_length=5, null=True, blank=True)
    postal_code = models.CharField(
        max_length=6,
        validators=[RegexValidator(regex=r'^\d{2}-\d{3}$', message='Postal code must be in the format xx-xxx.')]
    )
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)

    bank_country_code = models.CharField(max_length=2)
    bank_account_number = models.CharField(
        max_length=26,
        validators=[RegexValidator(regex=r'^\d{26}$', message='Bank account number must be exactly 26 digits.')]
    )
    bank_name = models.CharField(max_length=100)
    bank_swift = models.CharField(max_length=11)

    date_of_employment = models.DateField()
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        if not self.middle_name:
            return f'{self.first_name} {self.last_name}'
        return f'{self.first_name} {self.middle_name} {self.last_name}'
