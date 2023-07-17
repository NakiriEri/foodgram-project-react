import csv
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")
django.setup()



from recipes.models import Ingredient

def import_database(self):
    with open('/home/deveri/foodgram-project-react/data/ingredients.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            _, created = Ingredient.objects.get_or_create(
                name=row[0],
                measures=row[1],
            )
        print("Импорт успешно завершен")
