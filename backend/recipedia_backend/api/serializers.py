import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.validators import EmailValidator, RegexValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from core.constants import Limits, Messages
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
)

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиента."""

    measurement_unit = serializers.StringRelatedField(
        source="unit", read_only=True
    )

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов рецепта."""

    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.StringRelatedField(
        source="ingredient.unit", read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeIngredientWriteSerializer(serializers.Serializer):
    """Сериализатор для создания/изменения ингредиентов рецепта."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=Limits.AMOUNT_MIN, max_value=Limits.AMOUNT_MAX
    )

    class Meta:
        fields = ("id", "amount")


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя"""

    username = serializers.CharField(
        max_length=Limits.USERNAME_LENGTH,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message=Messages.USERNAME_ALREADY_EXISTS,
            ),
            RegexValidator(r"^[\w.@+-]+\Z"),
        ],
        required=True,
        write_only=False,
    )
    email = serializers.EmailField(
        max_length=Limits.EMAIL_LENGTH,
        validators=[
            EmailValidator(),
            UniqueValidator(
                queryset=User.objects.all(),
                message=Messages.EMAIL_ALREADY_EXISTS,
            ),
        ],
    )
    first_name = serializers.CharField(
        max_length=Limits.FIRST_NAME_LENGTH,
        required=True,
    )
    last_name = serializers.CharField(
        max_length=Limits.LAST_NAME_LENGTH,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "username",
        )
        readonly_feilds = ("id",)
        extra_kwargs = {"password": {"write_only": True}}


class CustomUserSerializer(UserSerializer):
    """Сериализатор для чтения профиля пользователя"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )
        read_only_fields = ("id", "is_subscribed")

    def get_is_subscribed(self, author: User) -> bool:
        """Возвращает признак, подписан ли текущий пользователь на автора."""
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return user.subscriptions.filter(author=author).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов рецепта."""

    class Meta:
        model = Tag
        fields = "__all__"


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""

    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        read_only=True, many=True, source="recipeingredient_set"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField(method_name="get_formatted_text")

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, recipe: Recipe) -> bool:
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe: Recipe) -> bool:
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return user.shopping_carts.filter(recipe=recipe).exists()

    def get_formatted_text(self, recipe: Recipe) -> str:
        return recipe.get_formatted_text()


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор краткой формы рецепта для избранного, подписок."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class Base64ImageField(serializers.ImageField):
    """Сериализатор картинки блюда."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/изменения рецепта."""

    ingredients = RecipeIngredientWriteSerializer(many=True, allow_empty=False)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, allow_empty=False
    )
    image = Base64ImageField(allow_null=False)
    name = serializers.CharField(max_length=Limits.RECIPE_NAME_LENGTH)
    cooking_time = serializers.IntegerField(
        min_value=Limits.COOKING_TIME_MIN, max_value=Limits.COOKING_TIME_MAX
    )

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def add_tags(self, recipe: Recipe, tags: list[Tag]):
        for tag in tags:
            recipe.tags.add(tag)

    def add_ingredients(self, recipe: Recipe, ingredients_data):
        ingredients_models = [
            RecipeIngredient(
                ingredient=item["id"], amount=item["amount"], recipe=recipe
            )
            for item in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(ingredients_models)

    def create(self, validated_data):
        """Создание рецепта."""

        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        user = self.context.get("request").user
        recipe = Recipe.objects.create(author=user, **validated_data)
        self.add_tags(recipe, tags)
        self.add_ingredients(recipe, ingredients)
        recipe.save()
        return recipe

    def update(self, recipe, validated_data):
        """Обновление рецепта."""

        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe.tags.clear()
        recipe.ingredients.clear()
        self.add_tags(recipe, tags)
        self.add_ingredients(recipe, ingredients)
        fields = ["image", "name", "text", "cooking_time"]
        for field in fields:
            setattr(recipe, field, validated_data.get(field))
        recipe.save()
        return recipe

    def validate(self, data):
        # check for repetiteve tags
        tags = data.get("tags")
        if not tags:
            raise serializers.ValidationError(Messages.NO_TAGS)
        if len(set(tags)) < len(tags):
            raise serializers.ValidationError(Messages.REPETITIVE_TAGS)
        # check for repetitive ingredients
        ingredients = data.get("ingredients")
        ingredient_ids = [x["id"] for x in ingredients]
        if len(set(ingredient_ids)) < len(ingredient_ids):
            raise serializers.ValidationError(Messages.REPETITIVE_INGREDIENTS)
        if not ingredients:
            raise serializers.ValidationError(
                "Recipe without ingredients forbidden"
            )
        return data

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance, context={"request": self.context.get("request")}
        ).data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки на автора"""

    class Meta:
        fields = ("user", "author")
        model = Subscription

        validators = (
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=("user", "author"),
                message=Messages.SUBSCRIPTION_ALREADY_EXISTS,
            ),
        )

    def validate(self, data):
        if data["user"] == data["author"]:
            raise serializers.ValidationError(
                Messages.CANNOT_SUBSCRIBE_TO_HIMSELF
            )
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения подписки на автора."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        read_only_fields = ("__all__",)

    def get_is_subscribed(self, author: User) -> bool:
        """Возвращает признак, подписан ли текущий пользователь на автора."""
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return user.subscriptions.filter(author=author).exists()

    def get_recipes(self, author: User):
        request = self.context.get("request")
        recipes_limit = int(request.query_params.get("recipes_limit", "0"))
        author_recipes = author.recipes.all()
        if recipes_limit:
            author_recipes = author_recipes[:recipes_limit]
        return RecipeMinifiedSerializer(
            author_recipes, many=True, context={"request": request}
        ).data

    def get_recipes_count(self, author: User) -> int:
        """Возвращает общее количество рецептов автора."""
        return author.recipes.count()


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в корзину покупок."""

    class Meta:
        fields = ("user", "recipe")
        model = ShoppingCart

        validators = (
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=("user", "recipe"),
                message=Messages.RECIPE_ALREADY_IN_SHOPPING_CART,
            ),
        )

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe, context={"request": self.context.get("request")}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в избранное."""

    class Meta:
        fields = ("user", "recipe")
        model = Favorite

        validators = (
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "recipe"),
                message=Messages.RECIPE_ALREADY_IN_FAVORITE,
            ),
        )

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe, context={"request": self.context.get("request")}
        ).data
