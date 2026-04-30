from django import forms
from .models import AdvertisementCourse

class AdvertisementCourseForm(forms.ModelForm):
    class Meta:
        model = AdvertisementCourse
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
