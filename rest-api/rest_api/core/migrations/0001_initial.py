# Generated by Django 5.1.1 on 2024-09-10 10:41

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('username', models.CharField(max_length=5, unique=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to=settings.AUTH_USER_MODEL)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='modified_%(class)s_set', to=settings.AUTH_USER_MODEL)),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('first_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(max_length=100)),
                ('identity_document', models.CharField(choices=[('PASSPORT', 'Passport'), ('ID_CARD', 'Identity Card')], max_length=20)),
                ('pesel', models.CharField(blank=True, max_length=11, null=True)),
                ('date_of_birth', models.DateField()),
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
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='modified_%(class)s_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='user',
            name='employee',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user', to='core.employee'),
        ),
    ]