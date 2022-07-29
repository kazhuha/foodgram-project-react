# Generated by Django 3.2 on 2022-07-29 15:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_alter_recipe_cooking_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0.1)], verbose_name='Количество'),
        ),
    ]
