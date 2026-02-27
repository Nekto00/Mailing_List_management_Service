from django.contrib import admin
from mailings.models import Client, Message, Mailing, MailingAttempt


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "owner")
    list_filter = ("owner",)
    search_fields = ("full_name", "email")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "owner")
    list_filter = ("owner",)
    search_fields = ("subject",)


class MailingAttemptInline(admin.TabularInline):
    model = MailingAttempt
    extra = 0
    readonly_fields = ("attempt_time", "status", "server_response")
    can_delete = False


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "start_time", "end_time", "status", "owner")
    list_filter = ("status", "owner")
    search_fields = ("message__subject",)
    filter_horizontal = ("recipients",)
    inlines = [MailingAttemptInline]
    readonly_fields = ("status",)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ("mailing", "attempt_time", "status")
    list_filter = ("status", "attempt_time")
    readonly_fields = ("attempt_time", "status", "server_response", "mailing")
