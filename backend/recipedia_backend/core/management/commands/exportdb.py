import csv
import os

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

MESSAGE_EXPORT_TABLE: str = "Экспорт таблицы {}"
MESSAGE_EXPORT_FINISHED: str = "Экспорт завершен."

TABLE_NAMES = (
    "tag",
    "ingredient",
    "unit",
    "recipe",
    "recipeingredient",
    "subscription",
    "favorite",
    "shoppingcart",
)


class Command(BaseCommand):
    help = "Экспорт данных из базы данных"

    def add_arguments(self, parser):
        parser.add_argument(
            "dir_name",
            type=str,
            help=("Наименование директории для записи результатов"),
        )

    def export_csv(self, model, file_name):
        opts = model._meta

        field_names = [field.name for field in opts.fields]
        # Write a first row with header information
        with open(file_name, mode="w", encoding="utf-8") as csv_file:
            writer = csv.writer(
                csv_file,
                delimiter=",",
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL,
            )
            writer.writerow(field_names)
            # Write data rows
            for obj in model.objects.all():
                row = []
                for field in field_names:
                    if field in {
                        "user",
                        "author",
                        "recipe",
                        "ingredient",
                        "unit",
                    }:
                        row.append(getattr(getattr(obj, field), "id"))
                    else:
                        row.append(getattr(obj, field))
                writer.writerow(row)

    def handle(self, *args, **options):
        dir_name = options["dir_name"]
        if not dir_name:
            dir_name = "."
        else:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
        for table in TABLE_NAMES:
            print(MESSAGE_EXPORT_TABLE.format(table))
            model = apps.get_model(
                app_label="recipes", model_name=table.lower()
            )
            self.export_csv(model, dir_name + "/" + table + ".csv")
            print(MESSAGE_EXPORT_FINISHED)

        user = get_user_model()
        print(MESSAGE_EXPORT_TABLE.format("user"))
        self.export_csv(user, dir_name + "/user.csv")
        print(MESSAGE_EXPORT_FINISHED)
