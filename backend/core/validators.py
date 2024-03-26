import re

from django.core.exceptions import ValidationError


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            'Имя пользователя не может быть "me"'
        )
    if not bool(re.match(r'^[\w.@+-]+$', value)):
        raise ValidationError(
            'Некорректные символы в username'
        )
    return value
