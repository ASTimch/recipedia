from django.contrib.auth.models import AbstractUser
from django.db import models

from core.constants import Limits


class User(AbstractUser):
    """
    Модель пользователя платформы.
    """

    username = models.CharField(
        verbose_name="Имя пользователя",
        max_length=Limits.USERNAME_LENGTH,
        unique=True,
    )

    email = models.EmailField(
        verbose_name="Email-адрес",
        max_length=Limits.EMAIL_LENGTH,
        unique=True,
    )

    first_name = models.CharField(
        verbose_name="Имя",
        max_length=Limits.FIRST_NAME_LENGTH,
    )

    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=Limits.LAST_NAME_LENGTH,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("id",)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
