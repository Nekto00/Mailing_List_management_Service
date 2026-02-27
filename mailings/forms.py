from django import forms
from django.utils import timezone

from mailings.models import Client, Message, Mailing


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["email", "full_name", "comment"]
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email"}
            ),
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ф.И.О."}
            ),
            "comment": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Комментарий", "rows": 3}
            ),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["subject", "body"]
        widgets = {
            "subject": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Тема письма"}
            ),
            "body": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Текст письма",
                    "rows": 5,
                }
            ),
        }


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ["start_time", "end_time", "message", "recipients"]
        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "end_time": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "message": forms.Select(attrs={"class": "form-control"}),
            "recipients": forms.SelectMultiple(
                attrs={"class": "form-control", "size": "10"}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            # Фильтруем сообщения и получателей только для текущего пользователя
            self.fields["message"].queryset = Message.objects.filter(owner=user)
            self.fields["recipients"].queryset = Client.objects.filter(owner=user)

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time:
            if start_time < timezone.now():
                raise forms.ValidationError("Дата начала не может быть в прошлом")

            if start_time >= end_time:
                raise forms.ValidationError(
                    "Дата начала должна быть раньше даты окончания"
                )

        return cleaned_data
