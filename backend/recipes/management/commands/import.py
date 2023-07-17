import csv
from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open(
            'recipes/management/commands/ingredients.csv', 
            'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                _, created = Ingredient.objects.get_or_create(
                    name=row[0],
                    measures=row[1]
                )
        print("Импорт успешно завершен")
