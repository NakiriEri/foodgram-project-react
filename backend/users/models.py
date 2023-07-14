from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    "Модели пользователя"
    ADMIN = 'admin'
    USER = 'user'

    ROLE_CHOICES = (
        (ADMIN, 'admin'),
        (USER, 'user'))

    username = models.CharField(max_length=150, unique=True,)
    email = models.EmailField(verbose_name='email',
                              unique=True, max_length=254,)
    role = models.CharField('Роли пользователей', default=USER,
                            choices=ROLE_CHOICES, max_length=40)
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False,
        null=False
    )
    confirmation_code = models.CharField(
        max_length=150,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f"{self.username}"


class UserFollowing(models.Model):
    "Модели подписки"
    user = models.ForeignKey(
        User,
        related_name='subscriber',
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='subscribing',
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подпиcки'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'], name='unique_user_author')
        ]
