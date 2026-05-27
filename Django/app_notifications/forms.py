from Django.utils.logger import log_debug
log_debug("Cargando forms de app_notifications")

from django import forms
from .models import Advertisement, AdvertisementCourse


class AdvertisementCourseForm(forms.ModelForm):
    class Meta:
        model = AdvertisementCourse
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ["content", "community", "status"]
        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "community": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }