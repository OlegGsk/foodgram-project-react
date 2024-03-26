# Generated by Django 4.2.11 on 2024-03-26 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_user_password_follow_unique_follow_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='unique_follow',
        ),
        migrations.RemoveConstraint(
            model_name='follow',
            name='prevent_self_follow',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.CheckConstraint(check=models.Q(('user', models.F('author')), _negated=True), name='prevent_self_follow'),
        ),
    ]