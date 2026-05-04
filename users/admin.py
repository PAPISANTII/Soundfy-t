from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'es_artista', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Perfil Soundfy', {
            'fields': ('foto_perfil', 'biografia', 'fecha_nacimiento', 'es_artista', 'seguidores')
        }),
    )