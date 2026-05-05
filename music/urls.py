from django.urls import path
from . import views

urlpatterns = [
    path('', views.vista_inicio, name='inicio'),
    path('buscar/', views.vista_buscar, name='buscar'),
    path('playlists/', views.vista_mis_playlists, name='mis_playlists'),
    path('playlists/crear/', views.vista_crear_playlist, name='crear_playlist'),
    path('playlists/<int:pk>/', views.vista_detalle_playlist, name='detalle_playlist'),
    path('cancion/subir/', views.vista_subir_cancion, name='subir_cancion'),
    path('cancion/<int:pk>/', views.vista_detalle_cancion, name='detalle_cancion'),
    path('cancion/<int:pk>/reproduccion/', views.vista_registrar_reproduccion, name='registrar_reproduccion'),
    path('cancion/<int:pk>/me-gusta/', views.vista_toggle_me_gusta, name='toggle_me_gusta'),
    path('cancion/<int:cancion_pk>/añadir/<int:playlist_pk>/', views.vista_añadir_a_playlist, name='añadir_a_playlist'),
    path('cancion/<int:pk>/editar/', views.vista_editar_cancion, name='editar_cancion'),
    path('cancion/<int:pk>/me-gusta-estado/', views.vista_me_gusta_estado, name='me_gusta_estado'),
    path('playlists/<int:playlist_pk>/eliminar/<int:cancion_pk>/', views.vista_eliminar_de_playlist, name='eliminar_de_playlist'),
]