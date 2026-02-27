from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.conf import settings
from django.db.models import Count, Q, Case, When, IntegerField


from mailings.models import Client, Message, Mailing, MailingAttempt, logger
from mailings.forms import ClientForm, MessageForm, MailingForm


@method_decorator(cache_page(settings.CACHE_MIDDLEWARE_SECONDS), name="dispatch")
class HomeView(ListView):
    """Главная страница с общей статистикой"""

    model = Mailing
    template_name = "mailings/home.html"
    context_object_name = "mailings"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Mailing.objects.filter(owner=self.request.user)
        return Mailing.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Общее количество рассылок
        context["total_mailings"] = Mailing.objects.count()

        # Количество активных рассылок
        now = timezone.now()
        context["active_mailings"] = Mailing.objects.filter(
            start_time__lte=now, end_time__gte=now, status="started"
        ).count()

        # Количество уникальных получателей
        context["total_clients"] = Client.objects.values("email").distinct().count()

        return context


# CRUD для клиентов
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailings/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = "mailings/client_detail.html"
    context_object_name = "client"

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "mailings/client_form.html"
    success_url = reverse_lazy("mailings:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Клиент успешно создан!")
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "mailings/client_form.html"
    success_url = reverse_lazy("mailings:client_list")

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Клиент успешно обновлен!")
        return super().form_valid(form)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "mailings/client_confirm_delete.html"
    success_url = reverse_lazy("mailings:client_list")

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Клиент успешно удален!")
        return super().delete(request, *args, **kwargs)


# CRUD для сообщений
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailings/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "mailings/message_detail.html"
    context_object_name = "message"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailings/message_form.html"
    success_url = reverse_lazy("mailings:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Сообщение успешно создано!")
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailings/message_form.html"
    success_url = reverse_lazy("mailings:message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Сообщение успешно обновлено!")
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailings/message_confirm_delete.html"
    success_url = reverse_lazy("mailings:message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Сообщение успешно удалено!")
        return super().delete(request, *args, **kwargs)


# CRUD для рассылок
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailings/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class MailingSendView(LoginRequiredMixin, View):
    """Контроллер для отправки рассылки"""

    def post(self, request, pk):
        print(f"\n{'=' * 60}")
        print(f"✅ ПОЛУЧЕН POST ЗАПРОС НА ОТПРАВКУ РАССЫЛКИ #{pk}")
        print(f"{'=' * 60}")
        print(f"Пользователь: {request.user}")
        print(f"CSRF токен: {request.POST.get('csrfmiddlewaretoken', 'НЕТ')}")

        try:
            # Получаем рассылку
            mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
            print(f"✅ Рассылка найдена: {mailing.message.subject}")
            print(f"Статус: {mailing.status}")
            print(f"Получателей: {mailing.recipients.count()}")

            # Проверяем статус
            mailing.update_status()
            print(f"Статус после update: {mailing.status}")

            if mailing.status != "started":
                print("❌ Рассылка не активна")
                messages.error(
                    request,
                    f"Рассылка не активна. Текущий статус: {mailing.get_status_display()}",
                )
                return redirect("mailings:mailing_detail", pk=pk)

            # Отправляем
            print("🚀 Запуск отправки...")
            success, result = mailing.send_mailing()

            print(f"Результат: {result}")

            if success:
                messages.success(request, f"✅ {result}")
            else:
                messages.error(request, f"❌ {result}")

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback

            traceback.print_exc()
            messages.error(request, f"❌ Ошибка: {str(e)}")

        print(f"{'=' * 60}\n")
        return redirect("mailings:mailing_detail", pk=pk)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailings/mailing_detail.html"
    context_object_name = "mailing"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        try:
            obj.update_status()  # Обновляем статус при просмотре
        except Exception as e:
            # Логируем ошибку, но не прерываем просмотр
            print(f"Ошибка при обновлении статуса: {e}")
        return obj


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.update_status()  # Устанавливаем начальный статус
        messages.success(self.request, "Рассылка успешно создана!")
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.update_status()
        messages.success(self.request, "Рассылка успешно обновлена!")
        return super().form_valid(form)


class MailingReportView(LoginRequiredMixin, ListView):
    """Контроллер для отображения отчетов по рассылкам"""

    model = Mailing
    template_name = "mailings/report.html"
    context_object_name = "mailings"

    def get_queryset(self):
        # Получаем все рассылки пользователя
        mailings = Mailing.objects.filter(owner=self.request.user)

        # Обновляем статусы
        for mailing in mailings:
            mailing.update_status()

        # Возвращаем рассылки с аннотациями
        return (
            Mailing.objects.filter(owner=self.request.user)
            .annotate(
                success_count=Count("attempts", filter=Q(attempts__status="success")),
                fail_count=Count("attempts", filter=Q(attempts__status="failed")),
            )
            .prefetch_related("recipients", "attempts")
            .order_by("-start_time")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Текущее время
        now = timezone.now()

        # Получаем все рассылки пользователя (уже с обновленными статусами)
        all_mailings = list(self.get_queryset())

        # Общее количество рассылок
        context["total_mailings"] = len(all_mailings)

        # Количество клиентов
        context["total_clients"] = Client.objects.filter(
            owner=self.request.user
        ).count()

        # Активные рассылки - используем обновленные статусы из queryset
        active_mailings = [
            m
            for m in all_mailings
            if m.status == "started" and m.start_time <= now <= m.end_time
        ]
        context["active_mailings"] = len(active_mailings)

        # Статистика по попыткам
        attempts = MailingAttempt.objects.filter(mailing__owner=self.request.user)
        context["success_attempts"] = attempts.filter(status="success").count()
        context["failed_attempts"] = attempts.filter(status="failed").count()

        # Добавляем текущее время в контекст
        context["now"] = now

        # Добавляем список активных рассылок для удобства
        context["active_mailings_list"] = active_mailings

        return context


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailings/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Рассылка успешно удалена!")
        return super().delete(request, *args, **kwargs)


class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = "mailings/attempt_list.html"
    context_object_name = "attempts"

    def get_queryset(self):
        # Показываем попытки только для рассылок текущего пользователя
        user_mailings = Mailing.objects.filter(owner=self.request.user)
        return MailingAttempt.objects.filter(mailing__in=user_mailings).order_by(
            "-attempt_time"
        )
