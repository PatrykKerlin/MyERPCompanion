from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.apps import apps
from faker import Faker
from decimal import Decimal
import random
import re
import string


class Command(BaseCommand):
    eu_countries = ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark',
                    'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy',
                    'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 'Poland', 'Portugal',
                    'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden']

    positions = ["Chief Executive Officer", "Chief Financial Officer", "Chief Operating Officer",
                 "IT Director", "Logistics Director", "Sales Manager", "Purchasing Manager", "Warehouse Manager",
                 "Customer Service Manager", "ERP Specialist", "WMS Specialist", "Logistics Specialist",
                 "Warehouse Specialist", "Purchasing Specialist", "Sales Specialist", "Customer Service Specialist",
                 "IT Specialist", "Quality Control Specialist", "Data Analyst", "Warehouse Worker", "Driver",
                 "Shipping Coordinator", "Warehouse Operator", "Forklift Operator", "IT Support"]

    departments = ["Management Department", "Finance Department", "Operations Department", "IT Department",
                   "Logistics Department", "Sales Department", "Purchasing Department", "Warehouse Department",
                   "Customer Service Department", "Quality Control Department", "Shipping Department",
                   "Marketing Department", "Production Planning Department", "Human Resources (HR) Department"]

    def handle(self, *args, **options):
        methods_to_run = [Command.populate_users, Command.populate_employees]

        results = set()
        for method in methods_to_run:
            result = method()
            results.add(result)

        if True in results:
            self.stdout.write(self.style.WARNING("Database populated with initial data!"))
        else:
            self.stdout.write(self.style.WARNING("No initial data was populated."))

    @staticmethod
    def populate_users():
        is_populated = False
        user = get_user_model()

        if user.objects.count() == 0:
            user.objects.create_superuser(
                login='admin',
                password='admin',
                employee=None,
            )
            is_populated = True

        return is_populated

    @staticmethod
    def populate_employees():
        is_populated = False
        employee = apps.get_model('core', 'Employee')
        user = get_user_model().objects.filter(id=1, is_superuser=True).first()

        if not user:
            return is_populated

        if employee.objects.count() == 0:
            fake = Faker()
            for _ in range(5):
                first_name = fake.first_name()
                last_name = fake.last_name()

                new_employee = employee(
                    first_name=first_name,
                    middle_name=fake.first_name() if fake.boolean() else None,
                    last_name=last_name,
                    phone_country_code='+{:02d}'.format(fake.random_int(min=1, max=99)),
                    phone_number=fake.random_number(digits=9, fix_len=True),
                    email=f'{first_name.lower()}.{last_name.lower()}@example.com',
                    street=fake.street_name(),
                    house_number=fake.building_number(),
                    apartment_number=fake.building_number() if fake.boolean() else None,
                    postal_code='{:02d}-{:03d}'.format(fake.random_int(min=0, max=99), fake.random_int(min=0, max=999)),
                    city=fake.city(),
                    country=random.choice(Command.eu_countries),
                    identity_document=random.choice(['passport', 'id_card']),
                    identity_document_number=''.join(random.choices(string.ascii_letters + string.digits, k=9)),
                    pesel=fake.random_number(digits=11, fix_len=True) if fake.boolean() else None,
                    date_of_birth=fake.date_of_birth(minimum_age=21, maximum_age=65),
                    bank_country_code=fake.country_code(),
                    bank_account_number=fake.random_number(digits=26, fix_len=True),
                    bank_name=re.split(r'[ ,]+', fake.company())[0] + ' Bank',
                    bank_swift=fake.swift8(),
                    date_of_employment=fake.date_between(start_date='-1y', end_date='today'),
                    position=random.choice(Command.positions),
                    department=random.choice(Command.departments),
                    salary=Decimal(random.uniform(3000, 15000)).quantize(Decimal('0.01'))
                )
                new_employee.save(user=user)
                is_populated = True

        return is_populated
