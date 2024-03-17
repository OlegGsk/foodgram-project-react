import csv
import os

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from csv file'

    def handle(self, *args, **options):
        file = os.path.join('..', 'data/ingredients.csv')
        with open(file, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                ingredient, created = Ingredient.objects.update_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
                ingredient.save()
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'Ингредиент "{ingredient.name}" добавлен'
                    ))
                else:
                    self.stdout.write(self.style.SUCCESS(
                        f'Ингредиент "{ingredient.name}" уже существует'
                    ))
        self.stdout.write(self.style.SUCCESS(
            'Импорт завершен'
        ))