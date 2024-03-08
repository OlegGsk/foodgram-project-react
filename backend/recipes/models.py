from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('Название', max_length=200)
    color = models.CharField('Цвет', max_length=7)
    slug = models.SlugField('Слаг', max_length=200, unique=True)
    
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
    is_favorited = models.BooleanField('В избранное', default=False)
    is_in_shopping_cart = models.BooleanField('В корзину', default=False)
    name = models.CharField('Название', max_length=200)
    image = models.ImageField('Картинка', upload_to='recipes/images/')
    text = models.TextField('Описание', max_length=500)
    ingredients = models.ManyToManyField('Ingredient',
                                         through='RecipeIngredient')
    tags = models.ManyToManyField('Tag', through='RecipeTag')
    cooking_time = models.PositiveSmallIntegerField('Время приготовления',
                                                    default=1)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    def validate_cooking_time(self):
        if self.cooking_time <= 0:
            raise models.ValidationError(
                'Время приготовления должно быть больше нуля')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField('Количество', default=1)

    def __str__(self):
        return self.ingredient.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return self.tag.name
