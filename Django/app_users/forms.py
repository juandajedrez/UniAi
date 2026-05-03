from django import forms
from django.contrib.auth.models import User

from app_class.models import Department, Program
from .models import Profile, SocialMedia
from Django.utils.logger import log_debug
log_debug("Cargando forms de app_users")

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.NumberInput(attrs={'placeholder':'Nombre usuario',
                                                              'class':'login_input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password',
                                                              'class':'login_input'}))

class RegisterForm(forms.ModelForm):
    # Campos adicionales para el perfil
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'First name',
            'class': 'form-control'
        })
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Last name',
            'class': 'form-control'
        })
    )
    role = forms.ChoiceField(
        choices=[("TEACHER", "Profesor"), ("ADMIN", "Administrativo"), ("STUDENT", "Estudiante"), ("IA", "IA")],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    birthday = forms.DateField(
        widget=forms.DateInput(attrs={
            'placeholder': 'YYYY-MM-DD',
            'class': 'form-control',
            'type': 'date'
        })
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

        widgets = {
            'username': forms.NumberInput(attrs={
                'placeholder': 'User name',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email',
                'class': 'form-control'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        widgets = {
            "username": forms.NumberInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# --- Formulario para editar perfil ---
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["birthday", "department", "program", "role", "semester"]
        widgets = {
            "birthday": forms.TextInput(attrs={"class": "form-control"}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "program": forms.Select(attrs={"class": "form-select"}),
            "role": forms.Select(attrs={"class": "form-select"}),
            "semester": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["birthday"].disabled = True
        self.fields["department"].disabled = True 
        self.fields["program"].disabled = True
        if self.instance and self.instance.role == "ADMINISTRATIVE":
            self.fields.pop("program")
        self.fields["role"].disabled = True 
        # Control del semestre
        if self.instance and self.instance.role == "STUDENT":
        # Mostrar semestre pero deshabilitado
            self.fields["semester"].disabled = True
        else:
        # Eliminar semestre del formulario si no es estudiante
            self.fields.pop("semester")

# --- Formulario para redes sociales ---
class SocialMediaForm(forms.ModelForm):
    class Meta:
        model = SocialMedia
        fields = ["name", "link"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "link": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://..."}),
        }

