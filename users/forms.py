from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario


class FormularioRegistro(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')
    fecha_nacimiento = forms.DateField(
        required=False,
        label='Fecha de nacimiento',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'fecha_nacimiento', 'password1', 'password2')
        labels = {
            'username': 'Nombre de usuario',
        }

    def guardar_usuario(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data['email']
        usuario.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if commit:
            usuario.save()
        return usuario


class FormularioLogin(AuthenticationForm):
    username = forms.CharField(label='Nombre de usuario')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


class FormularioEditarPerfil(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'biografia', 'fecha_nacimiento', 'foto_perfil')
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'biografia': 'Biografía',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'foto_perfil': 'Foto de perfil',
        }
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'biografia': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Cuéntanos algo sobre ti...'}),
        }