import os
from subprocess import Popen

from django.core.management.base import BaseCommand


def get_number():
    number = '3'
    if os.name == "nt":
        number = ''
    return number


number = get_number()

COMMANDS = [
    f'python{number} manage.py flush --noinput',
    f'python{number} manage.py migrate',
    f'python{number} manage.py import_ingredients',
    f'python{number} manage.py runserver']


class Command(BaseCommand):
    help = 'Run all import commands'

    def handle(self, *args, **options):
        for command in COMMANDS:
            p = Popen(command, shell=True)
            p.wait()
