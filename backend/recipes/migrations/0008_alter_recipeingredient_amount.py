# Generated by Django 4.2.11 on 2024-03-13 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_rename_ingredient_recipeingredient_ingredients'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Количество'),
        ),
    ]