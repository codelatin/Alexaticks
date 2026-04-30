from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from .models import Perfil, AsignacionSecretaria


class LoginForm(forms.Form):
    username = forms.CharField(
        label='', widget=forms.TextInput(attrs={
            'placeholder': '',
            'autocomplete': 'username',
            'class': 'login-input',
            'id': 'username'
        })
    )
    password = forms.CharField(
        label='', widget=forms.PasswordInput(attrs={
            'placeholder': '',
            'autocomplete': 'current-password',
            'class': 'login-input',
            'id': 'password'
        })
    )


class RegistroClienteForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Nombre', max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    last_name = forms.CharField(
        label='Apellido', max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )
    company_name = forms.CharField(
        label='Empresa', max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    country = forms.CharField(
        label='País', max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    phone = forms.CharField(
        label='Teléfono', max_length=30, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    preferred_language = forms.ChoiceField(
        label='Idioma preferido',
        choices=Perfil.IDIOMAS,
        initial='es',
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    secretaria = forms.ModelChoiceField(
        label='Asignar a secretaria',
        queryset=Perfil.objects.filter(role='secretaria', user__is_active=True),
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    class Meta:
        model = Perfil
        fields = ['company_name', 'country', 'phone', 'preferred_language']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo electrónico.')
        return email


class CambiarPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-input'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-input'})
        self.fields['new_password1'].label = 'Nueva contraseña'
        self.fields['new_password2'].label = 'Confirmar nueva contraseña'