# Generated by Django 5.0.1 on 2024-09-13 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_remove_shippingaddress_state_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingaddress',
            name='state',
            field=models.CharField(default=None, max_length=250),
        ),
        migrations.AddField(
            model_name='shippingaddress',
            name='zipcode',
            field=models.CharField(default=None, max_length=250),
        ),
    ]
