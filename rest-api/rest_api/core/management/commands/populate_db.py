import os
import json

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.apps import apps
from django.conf import settings


class Command(BaseCommand):
    payload_path = os.path.join(settings.BASE_DIR, 'core', 'management', 'commands', 'db_payload')
    core_payload_path = os.path.join(payload_path, 'core')
    business_payload_path = os.path.join(payload_path, 'business')

    def handle(self, *args, **options):
        superuser_added = self.add_superuser()

        if superuser_added:
            methods_to_run = [self.populate_languages, self.populate_labels_translations, self.populate_modules,
                              self.populate_pages, self.populate_page_labels, self.populate_images,
                              self.populate_page_images, self.populate_employees]

            user = get_user_model().objects.filter(id=1, is_superuser=True).first()

            for method in methods_to_run:
                method(user)

            self.stdout.write(self.style.WARNING("Database populated with initial data!"))
        else:
            self.stdout.write(self.style.WARNING("No initial data was populated."))

    def add_superuser(self):
        User = get_user_model()

        if User.objects.count() > 0:
            return False

        file_path = os.path.join(self.core_payload_path, 'superuser.json')
        with open(file_path, 'r') as file:
            data = json.load(file)
            User.objects.create_superuser(**data)

        return True

    def populate_languages(self, user):
        Language = apps.get_model('core', 'Language')

        file_path = os.path.join(self.core_payload_path, 'language.json')
        with open(file_path, 'r') as file:
            data = json.load(file)

            for attrs in data:
                new_language = Language(**attrs)
                new_language.save(user=user)

    def populate_labels_translations(self, user):
        Label = apps.get_model('core', 'Label')
        Translation = apps.get_model('core', 'Translation')
        LabelTranslations = apps.get_model('core', 'LabelTranslations')

        Language = apps.get_model('core', 'Language')
        lang_pl = Language.objects.filter(value='pl').first()
        lang_en = Language.objects.filter(value='en').first()

        file_path = os.path.join(self.core_payload_path, 'label_translation_label_translations.json')
        with open(file_path, 'r') as file:
            data = json.load(file)

            for label in data:
                new_label = Label(name=label['name'])
                new_label.save(user=user)

                for translation in label['translations']:
                    new_translation = Translation(
                        value=translation['value'],
                    )

                    if translation['language'] == 'en':
                        new_translation.language = lang_en
                    elif translation['language'] == 'pl':
                        new_translation.language = lang_pl

                    new_translation.save(user=user)

                    new_label_translation = LabelTranslations(
                        label=new_label,
                        translation=new_translation,
                    )

                    new_label_translation.save(user=user)

    def populate_modules(self, user):
        Module = apps.get_model('core', 'Module')
        Label = apps.get_model('core', 'Label')

        file_path = os.path.join(self.core_payload_path, 'module.json')
        with open(file_path, 'r') as file:
            data = json.load(file)

            for module in data:
                new_module = Module(
                    name=module['name'],
                    label=Label.objects.filter(name=module['label']).first(),
                )

                new_module.save(user=user)

    def populate_pages(self, user):
        Page = apps.get_model('core', 'Page')
        Module = apps.get_model('core', 'Module')
        Label = apps.get_model('core', 'Label')

        file_path = os.path.join(self.core_payload_path, 'page.json')
        with open(file_path, 'r') as file:
            data = json.load(file)

            for page in data:
                new_page = Page(
                    name=page['name'],
                    template=page['template'],
                    order=page['order'],
                )

                if page['label']:
                    new_page.label = Label.objects.filter(name=page['label']).first()
                if page['module']:
                    new_page.module = Module.objects.filter(name=page['module']).first()

                new_page.save(user=user)

    def populate_page_labels(self, user):
        PageLabels = apps.get_model('core', 'PageLabels')
        Label = apps.get_model('core', 'Label')
        Page = apps.get_model('core', 'Page')

        file_path = os.path.join(self.core_payload_path, 'page_labels.json')
        with open(file_path, 'r') as file:
            data = json.load(file)

            for page_labels in data:
                page = Page.objects.filter(name=page_labels['page']).first()
                for label_name in page_labels['labels']:
                    label = Label.objects.filter(name=label_name).first()
                    new_page_label = PageLabels(
                        page=page,
                        label=label
                    )

                    new_page_label.save(user=user)

    def populate_images(self, user):
        Image = apps.get_model('core', 'Image')

        file_path = os.path.join(self.core_payload_path, 'image.json')
        with open(file_path, 'r') as file:
            data = json.load(file)

            for image_attrs in data:
                new_image = Image(**image_attrs)
                new_image.save(user=user)

    def populate_page_images(self, user):
        PageImages = apps.get_model('core', 'PageImages')
        Page = apps.get_model('core', 'Page')
        Image = apps.get_model('core', 'Image')

        file_path = os.path.join(self.core_payload_path, 'page_images.json')
        with open(file_path, 'r') as file:
            data = json.load(file)

            for page_images in data:
                page = Page.objects.filter(name=page_images['page']).first()
                for image_name in page_images['images']:
                    image = Image.objects.filter(name=image_name).first()
                    new_page_image = PageImages(
                        page=page,
                        image=image
                    )

                    new_page_image.save(user=user)

    def populate_employees(self, user):
        Employee = apps.get_model('business', 'Employee')

        file_path = os.path.join(self.business_payload_path, 'employee.json')
        with open(file_path, 'r') as file:
            data = json.load(file)

            for employee_attrs in data:
                new_employee = Employee(**employee_attrs)
                new_employee.save(user=user)
