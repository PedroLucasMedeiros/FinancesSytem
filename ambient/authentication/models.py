from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import BaseModel

from .managers import CustomUserManager


class User(AbstractUser, BaseModel):
    # Remove o username: o identificador de login passa a ser o e-mail
    username = None

    email = models.EmailField("e-mail", unique=True)
    # Sobrescritos para serem obrigatórios (no AbstractUser são blank=True)
    first_name = models.CharField("nome", max_length=150)
    last_name = models.CharField("sobrenome", max_length=150)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]  # pedidos no createsuperuser

    # Redeclarados para garantir os managers do soft delete + e-mail
    objects = CustomUserManager()
    all_objects = CustomUserManager(alive_only=False)

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
        ordering = ["email"]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()