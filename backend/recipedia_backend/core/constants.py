from typing import Final


class Messages:
    """Текстовые сообщения приложения."""

    USERNAME_ALREADY_EXISTS: Final = "Такой username уже занят!"
    EMAIL_ALREADY_EXISTS: Final = "Пользователь c таким email уже существует!"
    EMPTY_FIELD_ERROR: Final = "Это поле не может быть пустым!"
    SUBSCRIPTION_ALREADY_EXISTS: Final = "Подписка на автора уже существует!"
    CANNOT_SUBSCRIBE_TO_HIMSELF: Final = "Нельзя подписаться на самого себя!"
    RECIPE_ALREADY_IN_SHOPPING_CART: Final = "Рецепт уже в корзине покупок!"
    RECIPE_ALREADY_IN_FAVORITE: Final = "Рецепт уже добавлен в избранное!"
    RECIPE_IS_NOT_IN_FAVORITE: Final = "Рецепт не содержится в избранном!"
    SUBSCRIPTION_IS_NOT_EXISTS: Final = "Подписки на автора не существует!"
    RECIPE_IS_NOT_IN_SHOPPING_CART: Final = "Рецепт не содержится в корзине!"
    LOAD_TABLE: Final = "Загрузка таблицы {}"
    LOAD_FINISHED: Final = "Загрузка завершена. Загружено {} записей"
    TABLE_UPDATE_FINISHED: Final = "Обновление таблицы завершено."
    MESSAGE_INGREDIENT: Final = "{}, {}"
    TABLE_IS_NOT_EMPTY: Final = (
        "Таблица {} не пустая!\n"
        "Вы можете:\n"
        "    1) Обновить все данные (все существующие записи будут удалены)\n"
        "    2) Дополнить таблицу несуществующими записями\n"
        "иначе) Оставить таблицу без изменения\n"
        "Ваш выбор (1 или 2): "
    )
    REPETITIVE_TAGS: Final = "Повторяющиеся тэги в рецепте!"
    REPETITIVE_INGREDIENTS: Final = "Повторяющиеся ингредиенты в рецепте!"
    NO_TAGS: Final = "Отсутствует поле tags!"


class Limits:
    """Числовые ограничения приложения."""

    # Настройки максимальной длины текстовых полей моделей
    INGREDIENT_NAME_LENGTH: int = 200
    UNIT_NAME_LENGTH: int = 200
    TAG_COLOR_LENGTH: int = 7
    TAG_NAME_LENGTH: int = 200
    TAG_SLUG_LENGTH: int = 200
    RECIPE_NAME_LENGTH: int = 200
    USERNAME_LENGTH: int = 150
    EMAIL_LENGTH: int = 254
    FIRST_NAME_LENGTH: int = 150
    LAST_NAME_LENGTH: int = 150
    PASSWORD_MAX_LENGTH: int = 150
    AMOUNT_MIN: int = 1
    AMOUNT_MAX: int = 32_000
    COOKING_TIME_MIN: int = 1
    COOKING_TIME_MAX: int = 32_000
