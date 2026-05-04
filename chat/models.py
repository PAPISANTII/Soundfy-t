from django.db import models
from users.models import Usuario


class SalaChat(models.Model):
    TIPOS = [
        ('general', 'General'),
        ('privado', 'Privado'),
    ]
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=10, choices=TIPOS, default='general')
    participantes = models.ManyToManyField(
        Usuario,
        related_name='salas_chat',
        blank=True
    )
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Sala de Chat'
        verbose_name_plural = 'Salas de Chat'

    def __str__(self):
        return self.nombre


class Mensaje(models.Model):
    sala = models.ForeignKey(
        SalaChat,
        on_delete=models.CASCADE,
        related_name='mensajes'
    )
    autor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='mensajes'
    )
    contenido = models.TextField()
    enviado_en = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['enviado_en']

    def __str__(self):
        return f'{self.autor.username}: {self.contenido[:50]}'