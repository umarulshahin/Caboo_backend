# Generated by Django 5.0.7 on 2024-09-09 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User_app', '0015_userwallet_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='tripdetails',
            name='service_type',
            field=models.CharField(default='bike', max_length=200),
            preserve_default=False,
        ),
    ]
