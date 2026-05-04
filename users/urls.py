from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.vista_registro, name='registro'),
    path('login/', views.vista_login, name='login'),
    path('logout/', views.vista_logout, name='logout'),
    path('perfil/editar/', views.vista_editar_perfil, name='editar_perfil'),
    path('perfil/<str:username>/', views.vista_perfil, name='perfil'),
    path('seguir/<str:username>/', views.vista_seguir_usuario, name='seguir_usuario'),
]