import csv

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Tag, Recipe, Ingredient, FavoriteList, ShoppingList
from .filters import RecipeFilter
from api.permissions import IsAdminOrAuthorOrReadOnly
from api.serializers import TagSerializer, RecipeViewSerializerGet,\
    IngredientSerializer, FavoriteRecipeSerializer, ShoppingListSerializer


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [IsAdminOrAuthorOrReadOnly]

    def main(self, request, pk, act, serialize):
        if request.method == 'POST':
            data = {'user': request.user.id, 'recipe': pk}
            serializer = serialize(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            user = request.user
            recipe = get_object_or_404(Recipe, id=pk)
            favorite = get_object_or_404(
                act, user=user, recipe=recipe
            )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        self.main(request=request, pk=pk,
                  act=FavoriteList,
                  serialize=FavoriteRecipeSerializer)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        self.main(request=request, pk=pk,
                  act=ShoppingList,
                  serialize=ShoppingListSerializer)

    @action(detail=False,  methods=['get'])
    def download_shopping_cart(self, request):
        ingredient_amount = (
            Ingredient.objects.filter(
                ingredients_in_recipe__recipe__in_baskets=request.user
            )
            .values_list('name', 'measurement_unit')
            .annotate(amount=Sum('ingredients_in_recipe__amount'))
        )
        response = HttpResponse(content_type="text/csv")
        response[
            'Content-Disposition'
        ] = 'attachment; filename=ingredients.csv'
        writer = csv.writer(response)
        for name, unit, amount in ingredient_amount:
            writer.writerow([name, amount, unit])
        return response
