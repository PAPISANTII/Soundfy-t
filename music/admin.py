from django.contrib import admin
from .models import Genero, Album, Cancion, Playlist, PlaylistCancion, MeGusta


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'artista', 'fecha_lanzamiento')
    search_fields = ('titulo', 'artista__username')


@admin.register(Cancion)
class CancionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'artista', 'album', 'reproducciones', 'es_publica', 'fecha_subida')
    search_fields = ('titulo', 'artista__username')
    list_filter = ('es_publica', 'genero')


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'propietario', 'es_publica', 'creada_en')
    search_fields = ('nombre', 'propietario__username')


admin.site.register(PlaylistCancion)
admin.site.register(MeGusta)