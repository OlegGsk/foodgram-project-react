# Generated by Django 4.2.11 on 2024-03-14 08:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_favorites_favorites_unique_favorite'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='favorites',
            name='unique_favorite',
        ),
    ]