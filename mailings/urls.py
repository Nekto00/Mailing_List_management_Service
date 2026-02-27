from django.urls import path
from mailings import views

app_name = "mailings"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    # ВАЖНО: Конкретные URL должны быть ПЕРЕД URL с параметрами
    path("attempts/", views.MailingAttemptListView.as_view(), name="attempt_list"),
    path("report/", views.MailingReportView.as_view(), name="report"),
    # Клиенты
    path("clients/", views.ClientListView.as_view(), name="client_list"),
    path("clients/create/", views.ClientCreateView.as_view(), name="client_create"),
    # URL с параметрами - после конкретных
    path("clients/<int:pk>/", views.ClientDetailView.as_view(), name="client_detail"),
    path(
        "clients/<int:pk>/update/",
        views.ClientUpdateView.as_view(),
        name="client_update",
    ),
    path(
        "clients/<int:pk>/delete/",
        views.ClientDeleteView.as_view(),
        name="client_delete",
    ),
    # Сообщения
    path("messages/", views.MessageListView.as_view(), name="message_list"),
    path("messages/create/", views.MessageCreateView.as_view(), name="message_create"),
    path(
        "messages/<int:pk>/", views.MessageDetailView.as_view(), name="message_detail"
    ),
    path(
        "messages/<int:pk>/update/",
        views.MessageUpdateView.as_view(),
        name="message_update",
    ),
    path(
        "messages/<int:pk>/delete/",
        views.MessageDeleteView.as_view(),
        name="message_delete",
    ),
    # Рассылки
    path("mailings/", views.MailingListView.as_view(), name="mailing_list"),
    path("mailings/create/", views.MailingCreateView.as_view(), name="mailing_create"),
    # ВАЖНО: send должен быть ПЕРЕД <int:pk>
    path(
        "mailings/<int:pk>/send/", views.MailingSendView.as_view(), name="mailing_send"
    ),
    # URL с параметрами - после send
    path(
        "mailings/<int:pk>/", views.MailingDetailView.as_view(), name="mailing_detail"
    ),
    path(
        "mailings/<int:pk>/update/",
        views.MailingUpdateView.as_view(),
        name="mailing_update",
    ),
    path(
        "mailings/<int:pk>/delete/",
        views.MailingDeleteView.as_view(),
        name="mailing_delete",
    ),
]
