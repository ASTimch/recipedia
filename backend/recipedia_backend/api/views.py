from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsAuthenticatedCreateOrAuthorUpdateOrReadOnly
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartSerializer,
    SubscribeSerializer,
    SubscriptionSerializer,
    TagSerializer,
)
from core.constants import Messages
from core.utils import ShoppingList
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    pagination_class = PageLimitPagination
    permission_classes = (IsAuthenticatedCreateOrAuthorUpdateOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        methods=["post", "delete"],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            data = {"user": user.id, "recipe": recipe.id}
            serializer = FavoriteSerializer(
                data=data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            qs = user.favorites.filter(recipe=recipe)
            if qs.exists():
                qs.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            return Response(
                data={"errors": Messages.RECIPE_IS_NOT_IN_FAVORITE},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=("get",),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        user = request.user
        filename = "recipedia_shopping_list_{}.txt".format(
            timezone.now().date()
        )
        shopping_list = ShoppingList.get_table(user)
        response = HttpResponse(
            shopping_list, content_type="text/plain; charset=utf-8"
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response


class SubscribeAPIView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        data = {"user": request.user.id, "author": id}
        serializer = SubscribeSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        subscribtion = serializer.save()
        return Response(
            SubscriptionSerializer(
                subscribtion.author, context={"request": request}
            ).data,
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscriptions = user.subscriptions.filter(author=author)
        if subscriptions.exists():
            subscriptions.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            data={"errors": Messages.SUBSCRIPTION_IS_NOT_EXISTS},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserSubscriptionAPIView(generics.ListAPIView):
    """Представление для вывода подписок текущего пользователя."""

    pagination_class = PageLimitPagination
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(followers__user=user).prefetch_related(
            "recipes"
        )


class ShoppingCartAPIView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        data = {"user": request.user.id, "recipe": id}
        serializer = ShoppingCartSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        shopping_carts = user.shopping_carts.filter(recipe=recipe)
        if shopping_carts.exists():
            shopping_carts.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": Messages.RECIPE_IS_NOT_IN_SHOPPING_CART},
            status=status.HTTP_400_BAD_REQUEST,
        )
