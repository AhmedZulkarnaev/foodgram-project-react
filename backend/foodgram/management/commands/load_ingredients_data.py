import csv

from django.core.management.base import BaseCommand

from foodgram.models import Ingredient
from foodgram_backend.settings import CSV_FILES_DIR


class Command(BaseCommand):
    help = 'Загрузка ингредиентов в базу данных'

    def handle(self, *args, **kwargs):
        with open(
            f'{CSV_FILES_DIR}/ingredients.csv', encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            next(reader)
            ingredients = [
                Ingredient(
                    name=row[0],
                    measurement_unit=row[1],
                )
                for row in reader
            ]
            Ingredient.objects.bulk_create(ingredients)
