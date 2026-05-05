from rest_framework import serializers
from .models import Cancion, Playlist, PlaylistCancion
from users.models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'foto_perfil', 'biografia', 'es_artista']


class CancionSerializer(serializers.ModelSerializer):
    artista = UsuarioSerializer(read_only=True)

    class Meta:
        model = Cancion
        fields = [
            'id', 'titulo', 'artista', 'portada',
            'archivo_audio', 'duracion', 'reproducciones',
            'fecha_subida', 'es_publica'
        ]


class PlaylistSerializer(serializers.ModelSerializer):
    propietario = UsuarioSerializer(read_only=True)
    canciones = CancionSerializer(many=True, read_only=True)

    class Meta:
        model = Playlist
        fields = [
            'id', 'nombre', 'descripcion', 'portada',
            'es_publica', 'creada_en', 'propietario', 'canciones'
        ]