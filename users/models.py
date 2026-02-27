from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Менеджер для модели пользователя"""

    def create_user(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет обычного пользователя
        """
        if not email:
            raise ValueError("Email должен быть указан")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет суперпользователя
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None  # Убираем поле username
    email = models.EmailField(unique=True, verbose_name="Email")
    avatar = models.ImageField(
        upload_to="users/avatars/", null=True, blank=True, verbose_name="Аватар"
    )
    phone = models.CharField(
        max_length=35, null=True, blank=True, verbose_name="Телефон"
    )
    country = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Страна"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Поля, которые будут запрашиваться при createsuperuser

    objects = UserManager()  # Подключаем менеджер

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
