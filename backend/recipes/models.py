from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.constance import (MAX_LENGTH_COLOR, MAX_LENGTH_MEASUREMENT_UNIT,
                            MAX_LENGTH_NAME, MAX_LENGTH_SLUG)
# from core.models import CreatedModel

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=MAX_LENGTH_NAME)
    measurement_unit = models.CharField('Единица измерения',
                                        max_length=MAX_LENGTH_MEASUREMENT_UNIT)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('Название', max_length=MAX_LENGTH_NAME)
    color = ColorField("Код цвета", default="#000000",
                       max_length=MAX_LENGTH_COLOR)
    slug = models.SlugField('Слаг', max_length=MAX_LENGTH_SLUG, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color'], name='unique_tag'
            ),
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='recipes')
    name = models.CharField('Название', max_length=MAX_LENGTH_NAME)
    image = models.ImageField('Картинка', upload_to='recipes/images')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField('Ingredient',
                                         through='RecipeIngredient')
    tags = models.ManyToManyField('Tag', through='RecipeTag')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(1,
                              'Время приготовления должно быть больше нуля'),
            MaxValueValidator(300,
                              'Не больше 300 минут'),])
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_ingredients',
                               null=True)
    ingredients = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                    related_name='recipe_ingredients')
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(1, 'Количество должно быть больше нуля'),
                    MaxValueValidator(10000, 'Не больше 10000')])

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return self.ingredients.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return self.tag.name


class CreatedUserRecipeModel(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='%(class)s')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='%(class)s')
    created_by = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingCart(CreatedUserRecipeModel):

    class Meta:
        verbose_name = 'Список покупок в корзине'


class Favorites(CreatedUserRecipeModel):

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'
