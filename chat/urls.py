from django.urls import path
from . import views

urlpatterns = [
    path('', views.vista_lista_salas, name='lista_salas'),
    path('<int:sala_id>/', views.vista_sala, name='sala'),
    path('nueva/<int:usuario_id>/', views.vista_crear_sala, name='crear_sala'),
    path('no-leidos/', views.vista_no_leidos, name='chat_no_leidos'),
]