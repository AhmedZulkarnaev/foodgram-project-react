import csv
import os

from django.core.management.base import BaseCommand, CommandError

from foodgram.models import Ingredient
from foodgram_backend.settings import CSV_FILES_DIR


class Command(BaseCommand):
    help = 'Загрузка ингредиентов в базу данных'

    def handle(self, *args, **kwargs):
        csv_file_path = os.path.join(CSV_FILES_DIR, 'ingredients.csv')
        try:
            with open(csv_file_path, encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)
                ingredients = [
                    Ingredient(
                        name=name,
                        measurement_unit=measurement_unit,
                    )
                    for name, measurement_unit in reader
                ]
                Ingredient.objects.bulk_create(ingredients)
        except FileNotFoundError:
            raise CommandError(f"File '{csv_file_path}' not found.")
        except Exception as e:
            raise CommandError(f"An error occurred: {e}")
