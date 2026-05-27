from Django.utils.logger import log_debug
log_debug("Cargando forms de app_calendar")

from app_users.models import Profile
from django import forms
from app_class.models import Course
from .models import Event, Advising, Event_recurrence
from django.contrib.auth.models import User


class AdvisingRequestForm(forms.ModelForm):
    class Meta:
        model = Advising
        fields = [
            "description",
            "startDateTime",
            "endDateTime",
            "location",
            "advisor",
        ]
        labels = {
            "description": "Descripción",
            "startDateTime": "Fecha y hora de inicio",
            "endDateTime": "Fecha y hora de finalización",
            "location": "Ubicación",
            "advisor": "Docente asesor",
        }
        widgets = {
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "startDateTime": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "endDateTime": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "advisor": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, "profile"):
            # Cursos donde el estudiante está inscrito
            courses = Course.objects.filter(students=user.profile)

            # Docentes (Profiles) que enseñan esos cursos
            teachers = Profile.objects.filter(courses_as_teacher__in=courses).distinct()

            # Asignar queryset filtrado al campo advisor
            self.fields["advisor"].queryset = teachers




class EventForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
        required=False  
    )
    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "startDateTime",
            "endDateTime",
            "location",
            "participants",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "startDateTime": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M"
            ),
            "endDateTime": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M"
            ), "location": forms.TextInput(attrs={"class": "form-control"}),
        }


class Event_recurrenceForm(forms.ModelForm):
    class Meta:
        model = Event_recurrence
        fields = [
            "title",
            "description",
            "startDateTime",
            "endDateTime",
            "location",
            "recurrenceRule",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "startDateTime": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "endDateTime": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "recurrenceRule": forms.Select(attrs={"class": "form-select"}),
        }
