from django.contrib.auth.models import AbstractUser
from django.db import models

from core.constance import MAX_LENGTH_EMAIL, MAX_LENGTH_USER_NAME
from core.validators import validate_username


class User(AbstractUser):
    email = models.EmailField(
        'Почта', max_length=MAX_LENGTH_EMAIL, unique=True
    )
    username = models.CharField(
        'Имя пользователя', max_length=MAX_LENGTH_USER_NAME, unique=True,
        validators=[validate_username])
    first_name = models.CharField('Имя', max_length=MAX_LENGTH_USER_NAME)
    last_name = models.CharField('Фамилия', max_length=MAX_LENGTH_USER_NAME)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-id']

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User, related_name='follower', on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User, related_name='following', on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_follow',
                violation_error_message='Нельзя подписаться на себя.'
            ),
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow',
                violation_error_message='Такая подписка уже существует.'
            )]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-author']

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
