# Generated by Django 4.2.11 on 2024-03-14 07:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_alter_recipeingredient_ingredients'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoppingcart',
            name='quantity',
        ),
    ]