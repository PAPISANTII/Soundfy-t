from django.db import models
from users.models import Usuario


class Genero(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Género'
        verbose_name_plural = 'Géneros'

    def __str__(self):
        return self.nombre


class Album(models.Model):
    titulo = models.CharField(max_length=200)
    artista = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='albumes'
    )
    portada = models.ImageField(upload_to='portadas/', null=True, blank=True)
    fecha_lanzamiento = models.DateField(null=True, blank=True)
    descripcion = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Álbum'
        verbose_name_plural = 'Álbumes'

    def __str__(self):
        return f'{self.titulo} - {self.artista.username}'


class Cancion(models.Model):
    titulo = models.CharField(max_length=200)
    artista = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='canciones'
    )
    album = models.ForeignKey(
        Album,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='canciones'
    )
    genero = models.ForeignKey(
        Genero,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    archivo_audio = models.FileField(upload_to='canciones/')
    portada = models.ImageField(upload_to='portadas_canciones/', null=True, blank=True)
    duracion = models.PositiveIntegerField(help_text='Duración en segundos', default=0)
    reproducciones = models.PositiveIntegerField(default=0)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    es_publica = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Canción'
        verbose_name_plural = 'Canciones'
        ordering = ['-fecha_subida']

    def __str__(self):
        return f'{self.titulo} - {self.artista.username}'


class Playlist(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    propietario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='playlists'
    )
    canciones = models.ManyToManyField(
        Cancion,
        through='PlaylistCancion',
        blank=True
    )
    portada = models.ImageField(upload_to='portadas_playlists/', null=True, blank=True)
    es_publica = models.BooleanField(default=True)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Playlist'
        verbose_name_plural = 'Playlists'

    def __str__(self):
        return f'{self.nombre} ({self.propietario.username})'


class PlaylistCancion(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    cancion = models.ForeignKey(Cancion, on_delete=models.CASCADE)
    orden = models.PositiveIntegerField(default=0)
    añadida_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Canción en Playlist'
        verbose_name_plural = 'Canciones en Playlist'
        ordering = ['orden']
        unique_together = ('playlist', 'cancion')


class MeGusta(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='me_gustas'
    )
    cancion = models.ForeignKey(
        Cancion,
        on_delete=models.CASCADE,
        related_name='me_gustas'
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Me Gusta'
        verbose_name_plural = 'Me Gustas'
        unique_together = ('usuario', 'cancion')