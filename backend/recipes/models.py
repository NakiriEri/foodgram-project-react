from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        db_index=True,
        max_length=50,
        blank=True
    )
    measures = models.CharField(
        max_length=50,
        verbose_name='Единица измерения',
        help_text='Единица измерения',
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        db_index=True,
        max_length=50,
        unique=True
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет',
        unique=True, )

    slug = models.SlugField(
        verbose_name='Идентификатор тега',
        max_length=50,
        unique=True
    )

    class Meta:
        """
        Добавляет русские название в админке.
        """
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Aвтор',
        blank=True,
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        db_index=True,
        max_length=50,
        blank=True, )
    image = models.ImageField(upload_to='recipes/images/',
                              verbose_name='Картинка',
                              blank=True,
                              )
    text = models.TextField(verbose_name='Текст рецепта',
                            blank=True,
                            )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientPass',
        verbose_name='Ингредиенты',
        blank=True

    )
    tags = models.ManyToManyField(
        Tag,
        through='TagPass',
        verbose_name='Тег',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        blank=True,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientPass(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name="recipe_pass"
    )

    amount = models.IntegerField(
        verbose_name='Количество ингредиентов',
        blank=True,
    )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name="recipe_pass"
                               )

    class Meta:
        verbose_name = 'Ингредиент и рецепт'
        verbose_name_plural = 'Ингредиенты и рецепты '
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_Ingredient_recipe')
        ]

    def __str__(self):
        return f'{self.ingredient} => {self.recipe}'


class TagPass(models.Model):
    """Промежуточная модель связи тега и рецепта."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Тег и рецепт'
        verbose_name_plural = 'Теги и рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'recipe'],
                name='unique_tag_recipe')
        ]

    def __str__(self):
        return f'{self.tag} => {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Избранное')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт', )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избраные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe')
        ]


class ShopCart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Корзина',
                             related_name='shopping_cart')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='shopping_cart')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopcart_user_recipe')
        ]
