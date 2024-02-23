from django.contrib import admin
from django.utils.safestring import mark_safe

from .forms import TagAdminForm
from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
    Unit,
)


class UnitAdmin(admin.ModelAdmin):
    list_display = ("pk", "name")


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "unit")
    search_fields = ("name",)
    list_filter = ("unit",)


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")
    form = TagAdminForm


class RecipeIngredientInlineAdmin(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "author",
        "get_tags",
        "cooking_time",
    )
    fields = (
        "author",
        "name",
        "tags",
        "cooking_time",
        "text",
        "image",
        "image_preview",
        "pub_date",
        "favorite_count",
    )
    inlines = [
        RecipeIngredientInlineAdmin,
    ]
    readonly_fields = ("image_preview", "favorite_count", "pub_date")
    search_fields = ("name", "author__first_name", "author__last_name")
    list_filter = ("tags",)
    save_on_top = True
    actions_on_top = True

    def image_preview(self, obj):
        if not obj.image:
            return ""
        return mark_safe(
            f'<img src="{obj.image.url}"  style="max-height: 100px;">'
        )

    image_preview.short_description = "Превью блюда"

    def favorite_count(self, obj):
        if obj.favorites.exists():
            return str(obj.favorites.count())
        return "0"

    favorite_count.short_description = "Добавлений в избранное"

    @admin.display(description="Тэги")
    def get_tags(self, obj) -> str:
        return ", ".join([tag.name for tag in obj.tags.all()])


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "recipe",
        "ingredient",
        "amount",
    )
    search_fields = (
        "recipe__name",
        "ingredient__name",
    )


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("pk", "recipe", "user")
    search_fields = (
        "recipe__name",
        "user__first_name",
        "user__last_name",
    )


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "author")
    search_fields = (
        "user__first_name",
        "user__last_name",
        "author__first_name",
        "author__last_name",
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")
    search_fields = (
        "user__first_name",
        "user__last_name",
        "recipe__name",
    )


admin.site.register(Unit, UnitAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Subscription, SubscribeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)

admin.site.site_header = "Административная панель Recipedia"
admin.site.index_title = "Настройки Recipedia"
admin.site.site_title = "Административная панель Recipedia"
