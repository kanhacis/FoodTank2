# Generated by Django 4.1.3 on 2023-11-06 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0003_alter_restaurant_veg_or_nonveg'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='veg_or_nonveg',
            field=models.CharField(choices=[('Vegetarian', 'Vegetarian'), ('Non-Vegetarian', 'Non-Vegetarian'), ('Both', 'Both')], max_length=255),
        ),
    ]
