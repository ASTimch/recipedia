from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.constants import Limits

User = get_user_model()


class Unit(models.Model):
    """Модель единиц измерения."""

    name = models.CharField(
        max_length=Limits.UNIT_NAME_LENGTH,
        unique=True,
        verbose_name="Единица измерения",
    )

    class Meta:
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиент для рецепта."""

    name = models.CharField(
        max_length=Limits.INGREDIENT_NAME_LENGTH,
        verbose_name="Ингредиент",
        help_text="Наименование ингредиента",
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="ingredients",
        verbose_name="Единица измерения",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name}, {self.unit.name}"


class Tag(models.Model):
    """Модель тэгов для рецептов."""

    name = models.CharField(
        max_length=Limits.TAG_NAME_LENGTH,
        verbose_name="Наименование тэга",
    )

    color = models.CharField(
        max_length=Limits.TAG_COLOR_LENGTH,
        default="#FFFFFF",
        verbose_name="Цвет тэга",
    )

    slug = models.SlugField(
        max_length=Limits.TAG_SLUG_LENGTH,
        unique=True,
        verbose_name="Слаг тэга",
    )

    class Meta:
        verbose_name = "Тэг рецепта"
        verbose_name_plural = "Тэги рецептов"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    name = models.CharField(
        max_length=Limits.RECIPE_NAME_LENGTH,
        verbose_name="Наименование рецепта",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )

    text = models.TextField(
        verbose_name="Описание рецепта",
    )

    image = models.ImageField(
        verbose_name="Картинка блюда",
        upload_to="recipes/images/",
        blank=True,
        null=True,
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        through_fields=("recipe", "ingredient"),
        verbose_name="Ингридиенты рецепта",
    )

    tags = models.ManyToManyField(Tag, verbose_name="Тэги", blank=False)

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления в минутах",
        validators=(
            MinValueValidator(Limits.COOKING_TIME_MIN),
            MaxValueValidator(Limits.COOKING_TIME_MAX),
        ),
    )

    pub_date = models.DateTimeField(
        verbose_name="Время добавления рецепта", auto_now_add=True
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.name

    def get_formatted_text(self):
        return "<br>".join(self.text.splitlines())


class RecipeIngredient(models.Model):
    """Ингредиент рецепта (с количеством)."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
    )

    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        validators=(
            MinValueValidator(Limits.AMOUNT_MIN),
            MaxValueValidator(Limits.AMOUNT_MAX),
        ),
    )

    class Meta:
        verbose_name = "Ингредиент рецепта"
        verbose_name_plural = "Ингредиенты рецепта"
        ordering = ("recipe",)


class Favorite(models.Model):
    """Избранные рецепты пользователей."""

    recipe = models.ForeignKey(
        Recipe,
        related_name="favorites",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    user = models.ForeignKey(
        User,
        related_name="favorites",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )

    class Meta:
        verbose_name = "Избранный рецепт пользователя."
        verbose_name_plural = "Избранные рецепты пользователей."
        ordering = ("user",)


class Subscription(models.Model):
    """Подписки на авторов."""

    user = models.ForeignKey(
        User,
        related_name="subscriptions",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )

    author = models.ForeignKey(
        User,
        related_name="followers",
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = (
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_user_author"
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F("user")),
                name="no_self_subscription",
            ),
        )
        ordering = ("user",)


class ShoppingCart(models.Model):
    """Корзина покупок."""

    user = models.ForeignKey(
        User,
        related_name="shopping_carts",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )

    recipe = models.ForeignKey(
        Recipe,
        related_name="in_shopping_carts",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзины покупок"
        constraints = (
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_recipe"
            ),
        )
        ordering = ("user",)
