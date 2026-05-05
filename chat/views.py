from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SalaChat, Mensaje
from users.models import Usuario


@login_required
def vista_lista_salas(request):
    salas = SalaChat.objects.filter(participantes=request.user).order_by('-creada_en')
    salas_data = []
    for sala in salas:
        otro = sala.otro_usuario(request.user)
        ultimo = sala.ultimo_mensaje()
        no_leidos = sala.mensajes_no_leidos(request.user)
        salas_data.append({
            'sala': sala,
            'otro': otro,
            'ultimo': ultimo,
            'no_leidos': no_leidos,
        })
    return render(request, 'chat/lista_salas.html', {'salas_data': salas_data})


@login_required
def vista_sala(request, sala_id):
    sala = get_object_or_404(SalaChat, pk=sala_id)
    if request.user not in sala.participantes.all():
        messages.error(request, 'No tienes acceso a esta sala.')
        return redirect('lista_salas')
    # Marcar mensajes como leídos al entrar
    sala.mensajes.filter(leido=False).exclude(autor=request.user).update(leido=True)
    otro = sala.otro_usuario(request.user)
    return render(request, 'chat/sala.html', {'sala': sala, 'otro': otro})


@login_required
def vista_crear_sala(request, usuario_id):
    otro = get_object_or_404(Usuario, pk=usuario_id)
    salas_comunes = SalaChat.objects.filter(
        tipo='privado', participantes=request.user
    ).filter(participantes=otro)
    if salas_comunes.exists():
        return redirect('sala', sala_id=salas_comunes.first().pk)
    sala = SalaChat.objects.create(
        nombre=f'{request.user.username} & {otro.username}',
        tipo='privado'
    )
    sala.participantes.add(request.user, otro)
    return redirect('sala', sala_id=sala.pk)


@login_required
def vista_no_leidos(request):
    """Endpoint para el badge del sidebar"""
    from django.http import JsonResponse
    total = 0
    salas = SalaChat.objects.filter(participantes=request.user)
    for sala in salas:
        total += sala.mensajes_no_leidos(request.user)
    return JsonResponse({'no_leidos': total})