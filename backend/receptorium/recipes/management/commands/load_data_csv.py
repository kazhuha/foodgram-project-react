import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Load ingridients from CSV"

    def handle(self, *args, **options):
        with open('data/ingredients.csv') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0].lower(),
                    measurement_unit=row[1].lower()
                )
        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена'))
