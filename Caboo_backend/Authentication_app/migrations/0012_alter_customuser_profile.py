# Generated by Django 5.0.7 on 2024-09-30 16:23

import Authentication_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Authentication_app', '0011_alter_customuser_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='profile',
            field=models.ImageField(max_length=250, upload_to=Authentication_app.models.upload_profile_image),
        ),
    ]
