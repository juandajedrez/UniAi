from django import forms
from .models import AdvertisementCourse
from Django.utils.logger import log_debug
log_debug("Cargando forms de app_notifications")

class AdvertisementCourseForm(forms.ModelForm):
    class Meta:
        model = AdvertisementCourse
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
