# Generated by Django 5.0.7 on 2024-07-25 15:49

import Authentication_app.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='OtpStorage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp', models.CharField(max_length=10)),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('username', models.CharField(max_length=30)),
                ('address', models.CharField(max_length=150)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('phone', models.CharField(max_length=10, unique=True)),
                ('profile', models.ImageField(max_length=250, upload_to=Authentication_app.models.upload_profile_image)),
                ('role', models.CharField(blank=True, max_length=50)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DriverData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aadhaar', models.CharField(max_length=15, unique=True)),
                ('vehicle_name', models.CharField(max_length=100)),
                ('vehicle_no', models.CharField(max_length=15)),
                ('rc_img', models.ImageField(max_length=250, upload_to=Authentication_app.models.upload_vehicle_image)),
                ('license', models.ImageField(max_length=250, upload_to=Authentication_app.models.upload_vehicle_image)),
                ('insurance', models.ImageField(max_length=250, upload_to=Authentication_app.models.upload_vehicle_image)),
                ('vehicle_photo', models.ImageField(max_length=250, upload_to=Authentication_app.models.upload_vehicle_image)),
                ('customuser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
