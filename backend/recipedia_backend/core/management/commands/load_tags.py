from csv import DictReader

from django.core.management import BaseCommand

from core.constants import Messages
from recipes.models import Tag


class Command(BaseCommand):
    help = "Загрузка данных из о тэгах из csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            help=("Наименование исходного файла"),
        )

    def handle(self, *args, **options):
        file_name = options["file"]
        if Tag.objects.exists():
            print(Messages.TABLE_IS_NOT_EMPTY.format("Tag"), end="")
            choice = input()
            if choice == "1":
                Tag.objects.all().delete()
            elif choice != "2":
                return
        print(Messages.LOAD_TABLE.format("Tag"))
        records_loaded = 0
        with open(file_name, encoding="utf-8") as csv_file:
            reader = DictReader(csv_file)
            tags = []
            for row in reader:
                try:
                    tags.append(Tag(**row))
                    records_loaded += 1
                except Exception as e:
                    print(self.style.NOTICE("Error for data {}".format(row)))
                    print(e)
            print(
                self.style.SUCCESS(
                    Messages.LOAD_FINISHED.format(records_loaded)
                )
            )
            Tag.objects.bulk_create(tags)
            print(self.style.SUCCESS(Messages.TABLE_UPDATE_FINISHED))
