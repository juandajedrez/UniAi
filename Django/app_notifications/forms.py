from django import forms
from .models import Notifications

class NotificationDetailForm(forms.ModelForm):
    class Meta:
        model = Notifications
        fields = ["content", "timestamp", "status"]
        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control", "readonly": "readonly"}),
            "timestamp": forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "status": forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
        }

class NotificationListForm(forms.Form):
    notifications = forms.ModelMultipleChoiceField(
        queryset=Notifications.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Mis notificaciones"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["notifications"].queryset = Notifications.objects.filter(user=user)
