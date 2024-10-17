import random
import re
import string
import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.apps import apps
from django.conf import settings
from django.core.files import File
from faker import Faker
from decimal import Decimal


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

    labels = [
        {'name': 'my_erp_companion'},
        {'name': 'login'},
        {'name': 'password'},
        {'name': 'index'},
        {'name': 'human_resources'},
        {'name': 'inventory'},
        {'name': 'new_employee'},
        {'name': 'new_item'},
    ]

    translations = {
        'my_erp_companion': {'en': 'MyERPCompanion', 'pl': 'MójAsystentERP'},
        'login': {'en': 'Login'},
        'password': {'en': 'Password', 'pl': 'Hasło'},
        'index': {'en': 'Index'},
        'human_resources': {'en': 'Human Resources', 'pl': 'Kadry'},
        'inventory': {'en': 'Inventory', 'pl': 'Magazyn'},
        'new_employee': {'en': 'New employee', 'pl': 'Nowy pracownik'},
        'new_item': {'en': 'New item', 'pl': 'Nowy detal'},
    }

    modules = [
        {'name': 'human_resources'},
        {'name': 'inventory'},
    ]

    pages = [
        {'name': 'login', 'template': 'core/login.html'},
        {'name': 'index', 'template': 'core/index.html'},
        {'name': 'new_employee', 'module': 'human_resources', 'template': 'business/add_employee.html', 'order': 1},
        {'name': 'new_item', 'module': 'inventory', 'template': 'business/add_item.html', 'order': 1},
    ]

    page_labels = {
        'login': ['my_erp_companion', 'login', 'password'],
        'index': ['my_erp_companion', 'index'],
        'new_employee': ['my_erp_companion', 'human_resources', 'new_employee'],
        'new_item': ['my_erp_companion', 'inventory', 'new_item'],
    }

    images = [
        {'name': 'login_bg_img', 'image': 'login-bg-img.jpg'}
    ]

    page_images = {
        'login': ['login_bg_img']
    }

    def handle(self, *args, **options):
        methods_to_run = [Command.populate_users, Command.populate_labels, Command.populate_translations,
                          Command.populate_modules, Command.populate_pages, Command.populate_page_labels,
                          Command.populate_label_translations, Command.populate_images, Command.populate_page_images,
                          Command.populate_employees, Command.populate_items]

        results = set()
        for method in methods_to_run:
            result = method()
            results.add(result)

        if True in results:
            self.stdout.write(self.style.WARNING("Database populated with initial data!"))
        else:
            self.stdout.write(self.style.WARNING("No initial data was populated."))

    @staticmethod
    def populate_modules():
        is_populated = False
        Module = apps.get_model('core', 'Module')
        Label = apps.get_model('core', 'Label')
        user = get_user_model().objects.filter(id=1, is_superuser=True).first()

        if not user:
            return is_populated

        if Module.objects.count() == 0:
            for module in Command.modules:
                new_module = Module(
                    name=module['name'],
                    label=Label.objects.get(name=module['name']),
                )

                new_module.save(user=user)

            is_populated = True

        return is_populated

    @staticmethod
    def populate_pages():
        is_populated = False
        Page = apps.get_model('core', 'Page')
        Module = apps.get_model('core', 'Module')
        Label = apps.get_model('core', 'Label')
        user = get_user_model().objects.filter(id=1, is_superuser=True).first()

        if not user:
            return is_populated

        if Page.objects.count() == 0:
            for page in Command.pages:
                new_page = Page(
                    name=page['name'],
                    template=page['template'],
                    label=Label.objects.get(name=page['name']),
                )

                if 'module' in page.keys():
                    new_page.module = Module.objects.get(name=page['module'])

                if 'order' in page.keys():
                    new_page.order = page['order']

                new_page.save(user=user)

            is_populated = True

        return is_populated

    @staticmethod
    def populate_labels():
        is_populated = False
        Label = apps.get_model('core', 'Label')
        user = get_user_model().objects.filter(id=1, is_superuser=True).first()

        if not user:
            return is_populated

        if Label.objects.count() == 0:
            for label_attrs in Command.labels:
                new_label = Label(**label_attrs)
                new_label.save(user=user)

            is_populated = True

        return is_populated

    @staticmethod
    def populate_translations():
        is_populated = False
        Translation = apps.get_model('core', 'Translation')
        user = get_user_model().objects.filter(id=1, is_superuser=True).first()

        if not user:
            return is_populated

        if Translation.objects.count() == 0:
            for translations in Command.translations.values():
                for language, value in translations.items():
                    new_translation = Translation(language=language, value=value)
                    new_translation.save(user=user)

            is_populated = True

        return is_populated

    @staticmethod
    def populate_page_labels():
        is_populated = False
        PageLabels = apps.get_model('core', 'PageLabels')
        Label = apps.get_model('core', 'Label')
        Page = apps.get_model('core', 'Page')
        user = get_user_model().objects.filter(id=1, is_superuser=True).first()

        if not user:
            return is_populated

        if PageLabels.objects.count() == 0:
            for page_name, label_names in Command.page_labels.items():
                page = Page.objects.get(name=page_name)
                for label_name in label_names:
                    label = Label.objects.get(name=label_name)
                    new_page_label = PageLabels(page=page, label=label)
                    new_page_label.save(user=user)

            is_populated = True

        return is_populated

    @staticmethod
    def populate_label_translations():
        is_populated = False
        LabelTranslations = apps.get_model('core', 'LabelTranslations')
        Label = apps.get_model('core', 'Label')
        Translation = apps.get_model('core', 'Translation')
        user = get_user_model().objects.filter(id=1, is_superuser=True).first()

        if not user:
            return is_populated

        if LabelTranslations.objects.count() == 0:
            for label_name, translations in Command.translations.items():
                label = Label.objects.get(name=label_name)
                for translation_value in translations.values():
                    translation = Translation.objects.get(value=translation_value)
                    new_label_translation = LabelTranslations(label=label, translation=translation)
                    new_label_translation.save(user=user)

            is_populated = True

        return is_populated

    @staticmethod
    def populate_images():
        is_populated = False
        Image = apps.get_model('core', 'Image')
        user = get_user_model().objects.filter(id=1, is_superuser=True).first()

        if not user:
            return is_populated

        if Image.objects.count() == 0:
            for image_attrs in Command.images:
                new_image = Image(**image_attrs)
                new_image.save(user=user)

            is_populated = True

        return is_populated

    @staticmethod
    def populate_page_images():
        is_populated = False
        PageImages = apps.get_model('core', 'PageImages')
        Page = apps.get_model('core', 'Page')
        Image = apps.get_model('core', 'Image')
        user = get_user_model().objects.filter(id=1, is_superuser=True).first()

        if not user:
            return is_populated

        if PageImages.objects.count() == 0:
            for page_name, images in Command.page_images.items():
                page = Page.objects.get(name=page_name)
                for image_name in images:
                    image = Image.objects.get(name=image_name)
                    new_page_image = PageImages(page=page, image=image)
                    new_page_image.save(user=user)

            is_populated = True

        return is_populated

    @staticmethod
    def populate_users():
        is_populated = False
        User = get_user_model()

        if User.objects.count() == 0:
            User.objects.create_superuser(
                login='admin',
                password='admin',
                employee=None,
            )
            is_populated = True

        return is_populated

    @staticmethod
    def populate_employees():
        is_populated = False
        Employee = apps.get_model('business', 'Employee')
        user = get_user_model().objects.filter(id=1, is_superuser=True).first()

        if not user:
            return is_populated

        if Employee.objects.count() == 0:
            fake = Faker()
            for _ in range(5):
                first_name = fake.first_name()
                last_name = fake.last_name()

                new_employee = Employee(
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

    @staticmethod
    def populate_items():
        is_populated = False
        Item = apps.get_model('business', 'Item')
        user = get_user_model().objects.filter(id=1, is_superuser=True).first()

        if not user:
            return is_populated

        if Item.objects.count() == 0:
            fake = Faker()
            for _ in range(10):
                name = fake.word().capitalize()
                index = fake.bothify(text='???-###')
                sku = fake.unique.bothify(text='???-#####')
                price = Decimal(random.uniform(10, 1000)).quantize(Decimal('0.01'))
                cost = Decimal(random.uniform(5, 500)).quantize(Decimal('0.01'))
                barcode = fake.unique.bothify(text='###########')  # Example for a 13-digit barcode
                stock_quantity = random.randint(0, 100)
                reorder_level = random.randint(10, 50)
                warehouse_location = fake.street_address()

                new_item = Item(
                    name=name,
                    index=index,
                    description=fake.sentence(),
                    price=price,
                    cost=cost,
                    sku=sku,
                    barcode=barcode,
                    weight=Decimal(random.uniform(0.1, 5.0)).quantize(Decimal('0.01')),
                    dimensions=f"{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(10, 100)}",
                    volume=Decimal(random.uniform(0.1, 1.0)).quantize(Decimal('0.001')),
                    stock_quantity=stock_quantity,
                    reorder_level=reorder_level,
                    warehouse_location=warehouse_location,
                    supplier_sku=fake.unique.bothify(text='???-#####'),
                    lead_time=random.randint(1, 30),
                    vat_rate=Decimal(23.00),
                    tax_category='Standard',
                )
                new_item.save(user=user)

            is_populated = True

        return is_populated
