# Generated by Django 3.2 on 2022-08-01 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_recipe_uniqe_recipe'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='recipeingredient',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='uniqe_ingredient'),
        ),
    ]
