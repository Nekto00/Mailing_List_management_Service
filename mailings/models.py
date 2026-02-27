from django.db import models
from config import settings
import logging

logger = logging.getLogger(__name__)


class Client(models.Model):
    """Модель получателя рассылки (клиента)"""

    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=255, verbose_name="Ф.И.О.")
    comment = models.TextField(verbose_name="Комментарий", blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        permissions = [
            ("can_view_all_clients", "Может просматривать всех клиентов"),
            ("can_block_client", "Может блокировать клиентов"),
        ]

    def __str__(self):
        return self.full_name


class Message(models.Model):
    """Модель сообщения для рассылки"""

    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        permissions = [
            ("can_view_all_messages", "Может просматривать все сообщения"),
            ("can_block_message", "Может блокировать сообщения"),
        ]

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    """Модель рассылки"""

    STATUS_CHOICES = [
        ("created", "Создана"),
        ("started", "Запущена"),
        ("completed", "Завершена"),
    ]

    start_time = models.DateTimeField(verbose_name="Дата и время начала")
    end_time = models.DateTimeField(verbose_name="Дата и время окончания")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="created", verbose_name="Статус"
    )
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, verbose_name="Сообщение"
    )
    recipients = models.ManyToManyField(Client, verbose_name="Получатели")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = [
            ("can_view_all_mailings", "Может просматривать все рассылки"),
            ("can_block_mailing", "Может блокировать рассылки"),
            ("can_disable_mailing", "Может отключать рассылки"),
        ]

    def clean(self):
        """Валидация дат только при создании или изменении рассылки"""
        # Пропускаем валидацию, если это существующий объект и мы не меняем даты
        if self.pk:  # Если объект уже существует в базе
            original = Mailing.objects.get(pk=self.pk)
            # Если даты не изменились, пропускаем валидацию
            if (
                original.start_time == self.start_time
                and original.end_time == self.end_time
            ):
                return

        # Валидация для новых объектов или при изменении дат
        if self.start_time and self.end_time:
            from django.utils import timezone

            now = timezone.now()

            # Проверяем, что дата начала не в прошлом (только для новых рассылок)
            if not self.pk and self.start_time < now:
                from django.core.exceptions import ValidationError

                raise ValidationError("Дата начала не может быть в прошлом")

            # Проверяем, что дата начала раньше даты окончания
            if self.start_time >= self.end_time:
                from django.core.exceptions import ValidationError

                raise ValidationError("Дата начала должна быть раньше даты окончания")

    def update_status(self):
        """Обновление статуса рассылки на основе текущего времени"""
        from django.utils import timezone

        now = timezone.now()

        if now < self.start_time:
            new_status = "created"
        elif self.start_time <= now <= self.end_time:
            new_status = "started"
        else:
            new_status = "completed"

        if self.status != new_status:
            self.status = new_status
            # Сохраняем без валидации, чтобы не проверять даты
            self.save(update_fields=["status"], skip_validation=True)

        return self.status

    def save(self, *args, **kwargs):
        """Переопределяем save с возможностью пропустить валидацию"""
        # Если есть аргумент skip_validation, пропускаем валидацию
        skip_validation = kwargs.pop("skip_validation", False)

        if not skip_validation:
            self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Рассылка "{self.message.subject}" от {self.start_time.strftime("%d.%m.%Y")}'

    def send_mailing(self):
        """
        Отправка рассылки всем получателям
        """
        from mailings.models import MailingAttempt
        from django.core.mail import send_mail
        import logging

        logger = logging.getLogger(__name__)

        # Обновляем статус
        self.update_status()

        # Проверяем, активна ли рассылка
        if self.status != "started":
            error_msg = (
                f"Рассылка не активна. Текущий статус: {self.get_status_display()}"
            )
            logger.warning(error_msg)
            return False, error_msg

        # Проверяем, есть ли получатели
        recipients = self.recipients.all()
        if not recipients:
            error_msg = "Нет получателей для рассылки"
            logger.warning(error_msg)
            return False, error_msg

        success_count = 0
        fail_count = 0

        # Отправляем каждому получателю
        for recipient in recipients:
            try:
                # Отправляем письмо
                result = send_mail(
                    subject=self.message.subject,
                    message=self.message.body,
                    from_email=None,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )

                if result == 1:
                    # Успешная отправка - СОЗДАЕМ ЗАПИСЬ
                    attempt = MailingAttempt.objects.create(
                        mailing=self,
                        status="success",
                        server_response=f"Письмо успешно отправлено на {recipient.email}",
                    )
                    print(
                        f"✅ Создана попытка #{attempt.id} для {recipient.email}"
                    )  # Отладка
                    success_count += 1
                else:
                    raise Exception(f"Письмо не отправлено (код: {result})")

            except Exception as e:
                # Ошибка отправки - СОЗДАЕМ ЗАПИСЬ
                error_text = str(e)[:200]
                attempt = MailingAttempt.objects.create(
                    mailing=self,
                    status="failed",
                    server_response=f"Ошибка для {recipient.email}: {error_text}",
                )
                print(
                    f"❌ Создана попытка #{attempt.id} с ошибкой для {recipient.email}"
                )  # Отладка
                fail_count += 1

        result_message = f"Отправлено: {success_count}, ошибок: {fail_count}"
        return True, result_message


class MailingAttempt(models.Model):
    """Модель попытки рассылки"""

    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("failed", "Не успешно"),
    ]

    attempt_time = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время попытки"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="Статус"
    )
    server_response = models.TextField(verbose_name="Ответ сервера", blank=True)
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Рассылка",
    )

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"

    def __str__(self):
        return f'Попытка {self.attempt_time.strftime("%d.%m.%Y %H:%M")} - {self.get_status_display()}'
