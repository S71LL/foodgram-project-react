import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

DATA_PATH = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        file_path = os.path.join(DATA_PATH, 'ingredients.csv')
        with open(file_path, mode='r') as file:
            reader = csv.reader(file)

            for row in reader:
                Ingredient.objects.get_or_create(name=row[0],
                                                 measurement_unit=row[1])
