# Generated by Django 4.2.11 on 2024-03-27 11:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_user_username'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['-id'], 'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
    ]
