from django.db import models
from users.models import Usuario


class SalaChat(models.Model):
    TIPO_CHOICES = [('privado', 'Privado'), ('grupo', 'Grupo')]
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='privado')
    participantes = models.ManyToManyField(Usuario, related_name='salas_chat')
    creada_en = models.DateTimeField(auto_now_add=True)

    def otro_usuario(self, usuario):
        """Devuelve el otro participante en un chat privado"""
        return self.participantes.exclude(pk=usuario.pk).first()

    def mensajes_no_leidos(self, usuario):
        """Cuenta mensajes no leídos para un usuario"""
        return self.mensajes.filter(leido=False).exclude(autor=usuario).count()

    def ultimo_mensaje(self):
        return self.mensajes.order_by('-enviado_en').first()

    def __str__(self):
        return self.nombre


class Mensaje(models.Model):
    sala = models.ForeignKey(SalaChat, on_delete=models.CASCADE, related_name='mensajes')
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    contenido = models.TextField()
    enviado_en = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.autor.username}: {self.contenido[:30]}'