from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from colorfield.fields import ColorField

User = get_user_model()

MIN_TIME = 1


class Tag(models.Model):
    """Теги"""
    title = models.CharField(max_length=200, verbose_name='Название', unique=True)
    color = ColorField(default='#FF0000', verbose_name='Цвет')
    slug = models.SlugField('Короткое название', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    """Ингридиенты"""
    title = models.CharField(max_length=200, unique=True, verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.title


class Recipe(models.Model):
    """Рецепт"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    title = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(
        'Картинка',
        upload_to='foodgram/',
        blank=True
    )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг',
        related_name='recipes'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                MIN_TIME,
                f'Минимальное время приготовления {MIN_TIME} минута .'
            )
        ]
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title[:15]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='Ингридиенты в рецепте'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        'Количество', validators=[MinValueValidator(1, 'не менее 1шт')],
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиент в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='ingredient_in_recepie'
            )
        ]

    def __str__(self):
        return f'Ингридиент {self.ingredient.name}' \
               f' содержится в рецепте {self.recipe.name}'


class ShoppingList(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppinglist',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppinglist',
        verbose_name='Пользователь'
    )
    date_created = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ['-date_created']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='shoppinglist'
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe} - {self.date_created}'


class FavoriteList(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь'
    )
    date_created = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ['-date_created']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favoritelist'
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe} - {self.date_created}'


class Subscription(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор рецептов'
    )
    date_created = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following'
            )
        ]
        ordering = ['-date_created']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (
            f'{self.date_created} '
            f'- {self.user.username} '
            f'подписался на {self.author.username}'
        )
