# Generated by Django 3.2 on 2022-07-29 20:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_alter_recipeingredient_amount'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['-pk'], 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
    ]