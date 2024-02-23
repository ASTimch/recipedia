from csv import DictReader

from django.core.management import BaseCommand

from core.constants import Messages
from recipes.models import Ingredient, Unit

# MESSAGE_LOAD_TABLE: str = "Загрузка таблицы {}"
# MESSAGE_LOAD_FINISHED: str = "Загрузка завершена. Загружено {} записей"
# MESSAGE_TABLE_UPDATE_FINISHED: str = "Обновление таблицы завершено."
# MESSAGE_INGREDIENT: str = "{}, {}"


class Command(BaseCommand):
    help = "Загрузка данных из об ингредиентах из csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            help=("Наименование исходного файла"),
        )

    def handle(self, *args, **options):
        file_name = options["file"]
        if Ingredient.objects.exists():
            print(Messages.TABLE_IS_NOT_EMPTY.format("Ingredient"), end="")
            choice = input()
            if choice == "1":
                Ingredient.objects.all().delete()
            elif choice != "2":
                return
        print(Messages.LOAD_TABLE.format("Ingredient"))
        records_loaded = 0
        with open(file_name, encoding="utf-8") as csv_file:
            reader = DictReader(csv_file)
            ingredients = []
            for row in reader:
                try:
                    unit, _ = Unit.objects.get_or_create(name=row["unit"])
                    ingredient = Ingredient(name=row["ingredient"], unit=unit)
                    ingredients.append(ingredient)
                    records_loaded += 1
                except Exception as e:
                    print(self.style.NOTICE("Error for data {}".format(row)))
                    print(e)
            print(
                self.style.SUCCESS(
                    Messages.LOAD_FINISHED.format(records_loaded)
                )
            )
            Ingredient.objects.bulk_create(ingredients)
            print(self.style.SUCCESS(Messages.TABLE_UPDATE_FINISHED))
