from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailings.models import Client, Message, Mailing


class Command(BaseCommand):
    help = "Создание групп и прав доступа"

    def handle(self, *args, **options):
        # Создаем группу Менеджеры
        managers_group, created = Group.objects.get_or_create(name="Менеджеры")

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" создана'))
        else:
            self.stdout.write('Группа "Менеджеры" уже существует')

        # Получаем content types для моделей
        client_ct = ContentType.objects.get_for_model(Client)
        message_ct = ContentType.objects.get_for_model(Message)
        mailing_ct = ContentType.objects.get_for_model(Mailing)

        # Собираем все права, которые нужно добавить группе
        permissions_to_add = []

        # Права для просмотра всех клиентов
        try:
            perm = Permission.objects.get(
                content_type=client_ct, codename="can_view_all_clients"
            )
            permissions_to_add.append(perm)
            self.stdout.write("Найдено право: can_view_all_clients")
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.WARNING("Право can_view_all_clients не найдено")
            )

        # Право для блокировки клиентов
        try:
            perm = Permission.objects.get(
                content_type=client_ct, codename="can_block_client"
            )
            permissions_to_add.append(perm)
            self.stdout.write("Найдено право: can_block_client")
        except Permission.DoesNotExist:
            self.stdout.write(self.style.WARNING("Право can_block_client не найдено"))

        # Права для просмотра всех сообщений
        try:
            perm = Permission.objects.get(
                content_type=message_ct, codename="can_view_all_messages"
            )
            permissions_to_add.append(perm)
            self.stdout.write("Найдено право: can_view_all_messages")
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.WARNING("Право can_view_all_messages не найдено")
            )

        # Право для блокировки сообщений
        try:
            perm = Permission.objects.get(
                content_type=message_ct, codename="can_block_message"
            )
            permissions_to_add.append(perm)
            self.stdout.write("Найдено право: can_block_message")
        except Permission.DoesNotExist:
            self.stdout.write(self.style.WARNING("Право can_block_message не найдено"))

        # Права для просмотра всех рассылок
        try:
            perm = Permission.objects.get(
                content_type=mailing_ct, codename="can_view_all_mailings"
            )
            permissions_to_add.append(perm)
            self.stdout.write("Найдено право: can_view_all_mailings")
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.WARNING("Право can_view_all_mailings не найдено")
            )

        # Право для блокировки рассылок
        try:
            perm = Permission.objects.get(
                content_type=mailing_ct, codename="can_block_mailing"
            )
            permissions_to_add.append(perm)
            self.stdout.write("Найдено право: can_block_mailing")
        except Permission.DoesNotExist:
            self.stdout.write(self.style.WARNING("Право can_block_mailing не найдено"))

        # Право для отключения рассылок
        try:
            perm = Permission.objects.get(
                content_type=mailing_ct, codename="can_disable_mailing"
            )
            permissions_to_add.append(perm)
            self.stdout.write("Найдено право: can_disable_mailing")
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.WARNING("Право can_disable_mailing не найдено")
            )

        # Добавляем все найденные права группе
        if permissions_to_add:
            managers_group.permissions.add(*permissions_to_add)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Добавлено {len(permissions_to_add)} прав группе "Менеджеры"'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING("Не найдено ни одного права для добавления")
            )

        # Выводим список всех прав группы
        self.stdout.write('\nТекущие права группы "Менеджеры":')
        for perm in managers_group.permissions.all():
            self.stdout.write(
                f"  - {perm.content_type.app_label}.{perm.codename}: {perm.name}"
            )
