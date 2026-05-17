from django import forms
from .models import Cancion, Album, Playlist


class FormularioSubirCancion(forms.ModelForm):
    class Meta:
        model = Cancion
        fields = ('titulo', 'archivo_audio', 'portada', 'es_publica')
        labels = {
            'titulo': 'Título',
            'archivo_audio': 'Archivo de audio (MP3, WAV)',
            'portada': 'Portada (opcional)',
            'es_publica': '¿Canción pública?',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Nombre de la canción'}),
            'archivo_audio': forms.FileInput(),
            'portada': forms.FileInput(),
        }


class FormularioCrearPlaylist(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ('nombre', 'descripcion', 'portada', 'es_publica')
        labels = {
            'nombre': 'Nombre de la playlist',
            'descripcion': 'Descripción',
            'portada': 'Portada (opcional)',
            'es_publica': '¿Playlist pública?',
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }