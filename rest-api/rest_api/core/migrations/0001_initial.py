# Generated by Django 5.1.1 on 2024-09-29 15:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('business', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('version', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField(blank=True, null=True)),
                ('modification_type', models.CharField(blank=True, choices=[('insert', 'insert'), ('update', 'update'), ('delete', 'delete')], max_length=6, null=True)),
                ('user_id', models.IntegerField()),
                ('login', models.CharField(max_length=6, null=True, unique=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('theme', models.CharField(choices=[('light', 'Light'), ('dark', 'dark')], max_length=5, null=True)),
                ('language', models.CharField(choices=[('en', 'English'), ('pl', 'Polish')], max_length=2, null=True)),
                ('created_by', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='employees', to='business.employee')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('modified_by', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField(blank=True, null=True)),
                ('modification_type', models.CharField(blank=True, choices=[('insert', 'insert'), ('update', 'update'), ('delete', 'delete')], max_length=6, null=True)),
                ('field_id', models.IntegerField()),
                ('name', models.CharField(max_length=25, unique=True)),
                ('created_by', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField(blank=True, null=True)),
                ('modification_type', models.CharField(blank=True, choices=[('insert', 'insert'), ('update', 'update'), ('delete', 'delete')], max_length=6, null=True)),
                ('image_id', models.IntegerField()),
                ('name', models.CharField(max_length=50, unique=True)),
                ('value', models.ImageField(upload_to='images/')),
                ('created_by', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField(blank=True, null=True)),
                ('modification_type', models.CharField(blank=True, choices=[('insert', 'insert'), ('update', 'update'), ('delete', 'delete')], max_length=6, null=True)),
                ('page_id', models.IntegerField()),
                ('name', models.CharField(max_length=25, unique=True)),
                ('template', models.CharField(max_length=255)),
                ('in_menu', models.BooleanField()),
                ('order', models.PositiveIntegerField()),
                ('created_by', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PageFields',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField(blank=True, null=True)),
                ('modification_type', models.CharField(blank=True, choices=[('insert', 'insert'), ('update', 'update'), ('delete', 'delete')], max_length=6, null=True)),
                ('pagefields_id', models.IntegerField()),
                ('created_by', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.field')),
                ('modified_by', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.page')),
            ],
            options={
                'verbose_name': 'Page-Fields',
                'db_table': 'core_page_fields',
                'unique_together': {('page', 'field')},
            },
        ),
        migrations.AddField(
            model_name='page',
            name='fields',
            field=models.ManyToManyField(limit_choices_to={'is_active': True}, related_name='pages', through='core.PageFields', to='core.field'),
        ),
        migrations.CreateModel(
            name='PageImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField(blank=True, null=True)),
                ('modification_type', models.CharField(blank=True, choices=[('insert', 'insert'), ('update', 'update'), ('delete', 'delete')], max_length=6, null=True)),
                ('pageimages_id', models.IntegerField()),
                ('created_by', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.image')),
                ('modified_by', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.page')),
            ],
            options={
                'verbose_name': 'Page-Images',
                'db_table': 'core_page_images',
                'unique_together': {('page', 'image')},
            },
        ),
        migrations.AddField(
            model_name='page',
            name='images',
            field=models.ManyToManyField(limit_choices_to={'is_active': True}, related_name='pages', through='core.PageImages', to='core.image'),
        ),
        migrations.CreateModel(
            name='Text',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField(blank=True, null=True)),
                ('modification_type', models.CharField(blank=True, choices=[('insert', 'insert'), ('update', 'update'), ('delete', 'delete')], max_length=6, null=True)),
                ('text_id', models.IntegerField()),
                ('language', models.CharField(choices=[('en', 'English'), ('pl', 'Polish')], max_length=2)),
                ('value', models.TextField()),
                ('created_by', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FieldTexts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField(blank=True, null=True)),
                ('modification_type', models.CharField(blank=True, choices=[('insert', 'insert'), ('update', 'update'), ('delete', 'delete')], max_length=6, null=True)),
                ('fieldtexts_id', models.IntegerField()),
                ('created_by', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.field')),
                ('modified_by', models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
                ('text', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.text')),
            ],
            options={
                'verbose_name': 'Field-Texts',
                'db_table': 'core_field_texts',
                'unique_together': {('field', 'text')},
            },
        ),
        migrations.AddField(
            model_name='field',
            name='texts',
            field=models.ManyToManyField(limit_choices_to={'is_active': True}, related_name='fields', through='core.FieldTexts', to='core.text'),
        ),
    ]
