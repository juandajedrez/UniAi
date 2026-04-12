from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Nombre usuario',
                                                              'class':'login_input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password',
                                                              'class':'login_input'}))
    
from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'login_input'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'class': 'login_input'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']

        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'User name',
                'class': 'login_input'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email',
                'class': 'login_input'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Las contraseñas no coinciden")
        return cleaned_data
