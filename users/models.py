from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    foto_perfil = models.ImageField(
        upload_to='fotos_perfil/', 
        null=True, 
        blank=True
    )
    biografia = models.TextField(max_length=500, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    es_artista = models.BooleanField(default=False)
    seguidores = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='siguiendo',
        blank=True
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.username