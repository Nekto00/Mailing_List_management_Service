from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from users.models import User


class UserRegisterForm(UserCreationForm):
    """Форма регистрации пользователя"""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Пароль"}
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Подтверждение пароля"}
        )
    )

    class Meta:
        model = User
        fields = (
            "email",
            "password1",
            "password2",
            "first_name",
            "last_name",
            "phone",
            "country",
        )
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Имя"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Фамилия"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Телефон"}
            ),
            "country": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Страна"}
            ),
        }


class UserProfileForm(UserChangeForm):
    """Форма редактирования профиля"""

    password = None  # Скрываем поле пароля

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone", "country", "avatar")
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-control", "readonly": "readonly"}
            ),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }
