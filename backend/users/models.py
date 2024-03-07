from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        'Почта', max_length=254, unique=True
    )
    username = models.CharField(
        'Имя пользователя', max_length=150, unique=True
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    password = models.CharField('Пароль', max_length=150)
    is_subscribed = models.BooleanField('Подписка', default=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
