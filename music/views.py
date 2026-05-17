from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from users import models
from .models import Cancion, Playlist, Genero, PlaylistCancion, MeGusta
from .forms import FormularioSubirCancion, FormularioCrearPlaylist
from users.models import Usuario
import mutagen


@login_required
def vista_inicio(request):
    canciones_recientes = Cancion.objects.filter(
        es_publica=True
    ).order_by('-fecha_subida')[:10]
    
    canciones_populares = Cancion.objects.filter(
        es_publica=True
    ).order_by('-reproducciones')[:10]

    return render(request, 'music/inicio.html', {
        'canciones_recientes': canciones_recientes,
        'canciones_populares': canciones_populares,
    })


@login_required
def vista_buscar(request):
    consulta = request.GET.get('q', '')
    canciones = []
    artistas = []

    if consulta:
        from users.models import Usuario
        canciones = Cancion.objects.filter(
            titulo__icontains=consulta,
            es_publica=True
        )[:20]
        artistas = Usuario.objects.filter(
            username__icontains=consulta
        )[:10]

    return render(request, 'music/buscar.html', {
        'consulta': consulta,
        'canciones': canciones,
        'artistas': artistas,
    })


@login_required
def vista_mis_playlists(request):
    playlists = request.user.playlists.all().order_by('-creada_en')
    canciones_gustadas = MeGusta.objects.filter(
        usuario=request.user
    ).select_related('cancion', 'cancion__artista').order_by('-creado_en')

    return render(request, 'music/mis_playlists.html', {
        'playlists': playlists,
        'canciones_gustadas': canciones_gustadas,
    })

@login_required
def vista_subir_cancion(request):
    if request.method == 'POST':
        formulario = FormularioSubirCancion(request.POST, request.FILES)
        if formulario.is_valid():
            cancion = formulario.save(commit=False)
            cancion.artista = request.user
            # Calcular duración automáticamente
            try:
                audio_mutagen = mutagen.File(cancion.archivo_audio)
                if audio_mutagen:
                    cancion.duracion = int(audio_mutagen.info.length)
            except Exception:
                cancion.duracion = 0
            cancion.save()
            messages.success(request, f'"{cancion.titulo}" subida correctamente.')
            return redirect('detalle_cancion', pk=cancion.pk)
    else:
        formulario = FormularioSubirCancion()

    return render(request, 'music/subir_cancion.html', {'formulario': formulario})


@login_required
def vista_detalle_cancion(request, pk):
    cancion = get_object_or_404(Cancion, pk=pk)
    # Incrementar reproducciones solo si no es el propio artista
    ya_gusta = MeGusta.objects.filter(
        usuario=request.user,
        cancion=cancion
    ).exists()
    playlists_usuario = request.user.playlists.all()

    return render(request, 'music/detalle_cancion.html', {
        'cancion': cancion,
        'ya_gusta': ya_gusta,
        'playlists_usuario': playlists_usuario,
    })


@login_required
def vista_registrar_reproduccion(request, pk):
    if request.method == 'POST':
        cancion = get_object_or_404(Cancion, pk=pk)
        if cancion.artista != request.user:
            cancion.reproducciones += 1
            cancion.save(update_fields=['reproducciones'])
        return JsonResponse({'ok': True, 'reproducciones': cancion.reproducciones})
    return JsonResponse({'ok': False}, status=405)


@login_required
def vista_toggle_me_gusta(request, pk):
    cancion = get_object_or_404(Cancion, pk=pk)
    me_gusta, creado = MeGusta.objects.get_or_create(
        usuario=request.user,
        cancion=cancion
    )
    if not creado:
        me_gusta.delete()
        return JsonResponse({'accion': 'eliminado'})
    return JsonResponse({'accion': 'añadido'})

@login_required
def vista_me_gusta_estado(request, pk):
    cancion = get_object_or_404(Cancion, pk=pk)
    ya_gusta = MeGusta.objects.filter(usuario=request.user, cancion=cancion).exists()
    return JsonResponse({'ya_gusta': ya_gusta})

@login_required
def vista_crear_playlist(request):
    if request.method == 'POST':
        formulario = FormularioCrearPlaylist(request.POST, request.FILES)
        if formulario.is_valid():
            playlist = formulario.save(commit=False)
            playlist.propietario = request.user
            playlist.save()
            messages.success(request, f'Playlist "{playlist.nombre}" creada.')
            return redirect('detalle_playlist', pk=playlist.pk)
    else:
        formulario = FormularioCrearPlaylist()

    return render(request, 'music/crear_playlist.html', {'formulario': formulario})

@login_required
def vista_eliminar_de_playlist(request, playlist_pk, cancion_pk):
    if request.method == 'POST':
        playlist = get_object_or_404(Playlist, pk=playlist_pk, propietario=request.user)
        PlaylistCancion.objects.filter(playlist=playlist, cancion_id=cancion_pk).delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=405)


@login_required
def vista_detalle_playlist(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    if not playlist.es_publica and playlist.propietario != request.user:
        messages.error(request, 'Esta playlist es privada.')
        return redirect('inicio')

    return render(request, 'music/detalle_playlist.html', {'playlist': playlist})


@login_required
def vista_añadir_a_playlist(request, cancion_pk, playlist_pk):
    cancion = get_object_or_404(Cancion, pk=cancion_pk)
    playlist = get_object_or_404(Playlist, pk=playlist_pk, propietario=request.user)
    _, creado = PlaylistCancion.objects.get_or_create(
        playlist=playlist,
        cancion=cancion
    )
    if creado:
        return JsonResponse({'ok': True, 'mensaje': f'Añadida a {playlist.nombre}'})
    return JsonResponse({'ok': False, 'mensaje': 'Ya estaba en la playlist'})

@login_required
def vista_editar_cancion(request, pk):
    cancion = get_object_or_404(Cancion, pk=pk, artista=request.user)
    if request.method == 'POST':
        formulario = FormularioSubirCancion(request.POST, request.FILES, instance=cancion)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Canción actualizada correctamente.')
            return redirect('detalle_cancion', pk=cancion.pk)
    else:
        formulario = FormularioSubirCancion(instance=cancion)
    return render(request, 'music/subir_cancion.html', {
        'formulario': formulario,
        'editando': True,
        'cancion': cancion,
    })
    
@login_required
def vista_buscar_ajax(request):
    consulta = request.GET.get('q', '').strip()
    resultados = []
    if len(consulta) >= 1:
        canciones = Cancion.objects.filter(
            titulo__icontains=consulta,
            es_publica=True
        ).select_related('artista')[:8]

        artistas = Usuario.objects.filter(
            username__icontains=consulta
        )[:5]

        for c in canciones:
            resultados.append({
                'tipo': 'cancion',
                'id': c.pk,
                'titulo': c.titulo,
                'artista': c.artista.username,
                'portada': c.portada.url if c.portada else '',
                'url': f'/cancion/{c.pk}/',
            })
        for a in artistas:
            resultados.append({
                'tipo': 'artista',
                'id': a.pk,
                'titulo': a.username,
                'artista': '',
                'portada': a.foto_perfil.url if a.foto_perfil else '',
                'url': f'/users/perfil/{a.username}/',
            })

    return JsonResponse({'resultados': resultados})
