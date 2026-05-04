from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import FormularioRegistro, FormularioLogin, FormularioEditarPerfil
from .models import Usuario


def vista_registro(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    
    if request.method == 'POST':
        formulario = FormularioRegistro(request.POST)
        if formulario.is_valid():
            usuario = formulario.guardar_usuario()
            login(request, usuario)
            messages.success(request, f'¡Bienvenido a Soundfy, {usuario.username}!')
            return redirect('inicio')
    else:
        formulario = FormularioRegistro()
    
    return render(request, 'users/registro.html', {'formulario': formulario})


def vista_login(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    
    if request.method == 'POST':
        formulario = FormularioLogin(request, data=request.POST)
        if formulario.is_valid():
            usuario = formulario.get_user()
            login(request, usuario)
            messages.success(request, f'¡Hola de nuevo, {usuario.username}!')
            return redirect('inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        formulario = FormularioLogin()
    
    return render(request, 'users/login.html', {'formulario': formulario})


@login_required
def vista_logout(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


@login_required
def vista_perfil(request, username):
    perfil = get_object_or_404(Usuario, username=username)
    canciones = perfil.canciones.filter(es_publica=True).order_by('-fecha_subida')[:10]
    playlists = perfil.playlists.filter(es_publica=True)
    es_propio = request.user == perfil
    ya_sigue = request.user.siguiendo.filter(pk=perfil.pk).exists()

    return render(request, 'users/perfil.html', {
        'perfil': perfil,
        'canciones': canciones,
        'playlists': playlists,
        'es_propio': es_propio,
        'ya_sigue': ya_sigue,
    })


@login_required
def vista_editar_perfil(request):
    if request.method == 'POST':
        formulario = FormularioEditarPerfil(
            request.POST,
            request.FILES,
            instance=request.user
        )
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil', username=request.user.username)
    else:
        formulario = FormularioEditarPerfil(instance=request.user)
    
    return render(request, 'users/editar_perfil.html', {'formulario': formulario})


@login_required
def vista_seguir_usuario(request, username):
    usuario_a_seguir = get_object_or_404(Usuario, username=username)
    
    if usuario_a_seguir == request.user:
        messages.error(request, 'No puedes seguirte a ti mismo.')
        return redirect('perfil', username=username)
    
    if request.user.siguiendo.filter(pk=usuario_a_seguir.pk).exists():
        request.user.siguiendo.remove(usuario_a_seguir)
        messages.info(request, f'Has dejado de seguir a {username}.')
    else:
        request.user.siguiendo.add(usuario_a_seguir)
        messages.success(request, f'Ahora sigues a {username}.')
    
    return redirect('perfil', username=username)