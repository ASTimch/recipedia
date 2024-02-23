import json
import os

from django.core.management import BaseCommand
from recipedia_backend.settings import INITIAL_DATA_DIR

from recipes.models import Tag

ALREADY_LOADED_MESSAGE: str = """
Таблица Tag не пустая!
Вы можете:
    1) Обновить все данные (все существующие записи будут удалены)
    2) Дополнить таблицу несуществующими записями
иначе) Оставить таблицу без изменения
Ваш выбор (1 или 2): """

MESSAGE_LOAD_TABLE: str = "Загрузка таблицы {}"
MESSAGE_LOAD_FINISHED: str = "Загрузка завершена. Загружено {} записей"
MESSAGE_TABLE_UPDATE_FINISHED: str = "Обновление таблицы завершено."
MESSAGE_INGREDIENT: str = "{}, {}"


class Command(BaseCommand):
    help = "Загрузка данных из init/tags.json"

    def handle(self, *args, **options):
        if Tag.objects.exists():
            print(ALREADY_LOADED_MESSAGE, end="")
            choice = input()
            if choice == "1":
                Tag.objects.all().delete()
            elif choice != "2":
                return
        print(MESSAGE_LOAD_TABLE.format("Tag"))
        records_loaded = 0
        with open(
            os.path.join(INITIAL_DATA_DIR, "init/tags.json"), encoding="utf-8"
        ) as jsonfile:
            tags_list = json.load(jsonfile)
            for tags in tags_list:
                try:
                    tag = Tag(**tags)
                    tag.save()
                    records_loaded += 1
                except Exception as e:
                    print(self.style.NOTICE("Error for data {}".format(tag)))
                    print(e)
            print(
                self.style.SUCCESS(
                    MESSAGE_LOAD_FINISHED.format(records_loaded)
                )
            )
        print(self.style.SUCCESS(MESSAGE_TABLE_UPDATE_FINISHED))
