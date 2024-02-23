import csv
import os

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.shortcuts import get_object_or_404

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
    Unit,
)

MESSAGE_IMPORT_TABLE: str = "Импорт таблицы {}"
MESSAGE_IMPORT_FINISHED: str = "Импорт завершен. Загружено {} записей."
ALREADY_LOADED_MESSAGE: str = """
Обновление всей базы данных!
Вы можете:
    1) Обновить все данные (все существующие записи будут удалены)
    2) Дополнить таблицы несуществующими записями
иначе) Оставить базу без изменения
Ваш выбор (1 или 2): """

TABLE_NAMES = (
    "tag",
    "unit",
    "ingredient",
    "recipe",
    "recipeingredient",
    "subscription",
    "favorite",
    "shoppingcart",
)


class Command(BaseCommand):
    help = "Импорт данных базы данных из csv файлов"

    def add_arguments(self, parser):
        parser.add_argument(
            "dir_name",
            type=str,
            help=("Наименование директории с исходными csv файлами"),
        )

    def get_model_by_name(self, model_name):
        if model_name in {
            "tag",
            "unit",
            "ingredient",
            "recipe",
            "recipeingredient",
            "subscription",
            "favorite",
            "shoppingcart",
        }:
            return apps.get_model(app_label="recipes", model_name=model_name)
        if model_name in {"user", "author"}:
            return get_user_model()
        return None

    def import_csv(self, model, file_name) -> int:
        def replace_id_by_objects(row):
            try:
                for field in row.keys():
                    child_model = self.get_model_by_name(field)
                    if child_model:
                        row[field] = get_object_or_404(
                            child_model, pk=row[field]
                        )
            except Exception as e:
                print(self.style.NOTICE("Error for data {}".format(row)))
                print(e)
            return True

        records_loaded = 0
        with open(file_name, encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            items = []
            for row in reader:
                if replace_id_by_objects(row):
                    items.append(model(**row))
                    records_loaded += 1
        model.objects.bulk_create(items)
        return records_loaded

    def handle(self, *args, **options):
        dir_name = options["dir_name"]
        if not dir_name:
            dir_name = "."
        else:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
        print(ALREADY_LOADED_MESSAGE, end="")
        choice = input()
        if choice == "1":
            ShoppingCart.objects.all().delete()
            Favorite.objects.all().delete()
            Subscription.objects.all().delete()
            RecipeIngredient.objects.all().delete()
            Recipe.objects.all().delete()
            Ingredient.objects.all().delete()
            Unit.objects.all().delete()
            Tag.objects.all().delete()
            # User.object.all().delete()

        elif choice != "2":
            return
        for table in TABLE_NAMES:
            model = self.get_model_by_name(table)
            print(MESSAGE_IMPORT_TABLE.format(table))
            records_loaded = self.import_csv(
                model, os.path.join(dir_name, table + ".csv")
            )
            print(
                self.style.SUCCESS(
                    MESSAGE_IMPORT_FINISHED.format(records_loaded)
                )
            )
