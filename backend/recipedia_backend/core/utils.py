from django.db.models import Sum
from django.utils import timezone
from tabulate import tabulate

from recipes.models import RecipeIngredient


class ShoppingList:
    """Класс для генерации списка покупок пользователя"""

    TITLE: str = "Список покупок {first_name} {last_name}\n" "от {date}\n"
    HEADERS = ("Ингредиент", "Количество", "Ед.изм")

    @classmethod
    def get_table(cls, user) -> str:
        """Возвращает список покупок пользователя user в табличном виде"""
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__in_shopping_carts__user=user
            )
            .values("ingredient__name", "ingredient__unit__name")
            .annotate(amount=Sum("amount"))
        )
        ingredients_table = (
            (x["ingredient__name"], x["amount"], x["ingredient__unit__name"])
            for x in ingredients
        )
        title = cls.TITLE.format(
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            date=timezone.now(),
        )
        table = tabulate(
            ingredients_table, headers=cls.HEADERS, tablefmt="orgtbl"
        )
        return title + table
