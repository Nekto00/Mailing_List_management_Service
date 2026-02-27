from django.core.management.base import BaseCommand
from django.utils import timezone
from mailings.models import Mailing
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Отправка активных рассылок'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mailing_id',
            type=int,
            help='ID конкретной рассылки для отправки'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительная отправка даже если рассылка не активна'
        )

    def handle(self, *args, **options):
        mailing_id = options.get('mailing_id')
        force = options.get('force', False)

        self.stdout.write(self.style.SUCCESS('🚀 Запуск отправки рассылок...'))

        if mailing_id:
            # Отправка конкретной рассылки
            self.send_single_mailing(mailing_id, force)
        else:
            # Отправка всех активных рассылок
            self.send_all_active_mailings()

    def send_single_mailing(self, mailing_id, force=False):
        """Отправка одной рассылки по ID"""
        try:
            # Получаем рассылку
            mailing = Mailing.objects.select_related('message').prefetch_related('recipients').get(pk=mailing_id)

            self.stdout.write(f'\n📧 Обработка рассылки #{mailing.id}: {mailing.message.subject}')
            self.stdout.write(f'  Текущий статус: {mailing.get_status_display()}')
            self.stdout.write(f'  Получателей: {mailing.recipients.count()}')

            # Обновляем статус
            old_status = mailing.status
            mailing.update_status()

            if old_status != mailing.status:
                self.stdout.write(f'  Статус обновлен: {old_status} -> {mailing.status}')

            # Проверяем возможность отправки
            if mailing.status != 'started' and not force:
                self.stdout.write(self.style.WARNING(
                    f'\n⚠️ Рассылка #{mailing_id} не активна.'
                    f'\n   Текущий статус: {mailing.get_status_display()}'
                    f'\n   Используйте --force для принудительной отправки'
                ))
                return

            if force and mailing.status != 'started':
                self.stdout.write(self.style.WARNING(
                    f'  ⚠️ Принудительная отправка рассылки со статусом {mailing.status}'
                ))

            # Отправляем
            success, message = mailing.send_mailing()

            if success:
                self.stdout.write(self.style.SUCCESS(f'\n✅ {message}'))
            else:
                self.stdout.write(self.style.ERROR(f'\n❌ {message}'))

        except Mailing.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'\n❌ Рассылка с ID {mailing_id} не найдена'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Ошибка: {str(e)}'))

    def send_all_active_mailings(self):
        """Отправка всех активных рассылок"""
        now = timezone.now()

        # Получаем активные рассылки
        mailings = Mailing.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            status='started'
        ).select_related('message').prefetch_related('recipients')

        count = mailings.count()
        self.stdout.write(f'\n📊 Найдено активных рассылок: {count}')

        if count == 0:
            self.stdout.write(self.style.WARNING('⚠️ Нет активных рассылок для отправки'))
            return

        success_total = 0
        fail_total = 0

        for mailing in mailings:
            self.stdout.write(f'\n📧 Обработка рассылки #{mailing.id}: {mailing.message.subject}')
            self.stdout.write(f'  Получателей: {mailing.recipients.count()}')

            try:
                success, message = mailing.send_mailing()

                if success:
                    self.stdout.write(self.style.SUCCESS(f'  ✅ {message}'))
                    # Парсим результат
                    if 'Отправлено:' in message:
                        import re
                        numbers = re.findall(r'\d+', message)
                        if len(numbers) >= 2:
                            success_total += int(numbers[0])
                            fail_total += int(numbers[1])
                else:
                    self.stdout.write(self.style.ERROR(f'  ❌ {message}'))
                    fail_total += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Ошибка: {str(e)}'))
                fail_total += 1

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'ИТОГО: Успешно отправлено: {success_total}, ошибок: {fail_total}'))