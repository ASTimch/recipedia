from django.urls import include, path, re_path
from rest_framework.routers import SimpleRouter

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartAPIView,
    SubscribeAPIView,
    TagViewSet,
    UserSubscriptionAPIView,
)

router = SimpleRouter()
router.register("ingredients", IngredientViewSet)
router.register("tags", TagViewSet)
router.register("recipes", RecipeViewSet)

urlpatterns = [
    re_path(
        r"^users/(?P<id>[^/.]+)/subscribe/$",
        SubscribeAPIView.as_view(),
        name="subscribe",
    ),
    path(
        "users/subscriptions/",
        UserSubscriptionAPIView.as_view(),
        name="subscriptions",
    ),
    re_path(
        r"^recipes/(?P<id>[^/.]+)/shopping_cart/$",
        ShoppingCartAPIView.as_view(),
        name="shopping_cart",
    ),
    re_path("", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.authtoken")),
    path("", include(router.urls)),
]
