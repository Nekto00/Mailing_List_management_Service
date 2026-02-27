from django.contrib.auth import login, logout
from django.contrib.auth.views import (
    LoginView as BaseLoginView,
    LogoutView as BaseLogoutView,
)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from users.forms import UserRegisterForm, UserProfileForm
from users.models import User


class RegisterView(CreateView):
    """Контроллер регистрации пользователя"""

    model = User
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("mailings:home")


class LoginView(BaseLoginView):
    """Контроллер авторизации пользователя"""

    template_name = "users/login.html"

    def get_success_url(self):
        return reverse_lazy("mailings:home")


class LogoutView(BaseLogoutView):
    """Контроллер выхода пользователя"""

    pass


class ProfileView(LoginRequiredMixin, DetailView):
    """Контроллер просмотра профиля"""

    model = User
    template_name = "users/profile.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        return self.request.user


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Контроллер редактирования профиля"""

    model = User
    form_class = UserProfileForm
    template_name = "users/profile_edit.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy("users:profile")
