from django.contrib import admin
from .models import SalaChat, Mensaje


@admin.register(SalaChat)
class SalaChatAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'creada_en')
    list_filter = ('tipo',)


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('autor', 'sala', 'contenido', 'enviado_en', 'leido')
    list_filter = ('sala', 'leido')
    search_fields = ('autor__username', 'contenido')