from django import forms
from .models import Cancion, Album, Playlist


class FormularioSubirCancion(forms.ModelForm):
    class Meta:
        model = Cancion
        fields = ('titulo', 'album', 'genero', 'archivo_audio', 'portada', 'es_publica')
        labels = {
            'titulo': 'Título',
            'album': 'Álbum (opcional)',
            'genero': 'Género',
            'archivo_audio': 'Archivo de audio (MP3, WAV)',
            'portada': 'Portada (opcional)',
            'es_publica': '¿Canción pública?',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Nombre de la canción'}),
        }

    def __init__(self, usuario, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['album'].queryset = Album.objects.filter(artista=usuario)
        self.fields['album'].empty_label = 'Sin álbum'


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