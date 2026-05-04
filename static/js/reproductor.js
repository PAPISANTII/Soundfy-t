const audio = document.getElementById('audio-elemento');
const btnPlayPausa = document.getElementById('btn-play-pause');
const iconoPlay = document.getElementById('icono-play');
const iconoPausa = document.getElementById('icono-pausa');
const barraProgreso = document.getElementById('barra-progreso');
const tiempoActual = document.getElementById('tiempo-actual');
const tiempoTotal = document.getElementById('tiempo-total');
const barraVolumen = document.getElementById('barra-volumen');
const reproductorTitulo = document.getElementById('reproductor-titulo');
const reproductorArtista = document.getElementById('reproductor-artista');
const reproductorPortada = document.getElementById('reproductor-portada');
const btnAnterior = document.getElementById('btn-anterior');
const btnSiguiente = document.getElementById('btn-siguiente');

// ── Cola ──────────────────────────────────────────────────────
let colaActual = [];
let indiceActual = -1;
let reproduccionContada = false;

// ── Volumen persistente ───────────────────────────────────────
const volumenGuardado = sessionStorage.getItem('volumen');
audio.volume = volumenGuardado !== null ? volumenGuardado / 100 : 1;
barraVolumen.value = volumenGuardado !== null ? volumenGuardado : 100;

// ── Helpers ───────────────────────────────────────────────────
function formatearTiempo(s) {
    if (isNaN(s)) return '0:00';
    return `${Math.floor(s/60)}:${String(Math.floor(s%60)).padStart(2,'0')}`;
}
function mostrarPausa() {
    iconoPlay.classList.add('oculto');
    iconoPausa.classList.remove('oculto');
}
function mostrarPlay() {
    iconoPlay.classList.remove('oculto');
    iconoPausa.classList.add('oculto');
}
function obtenerCsrf() {
    const c = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    return c ? c.split('=')[1] : '';
}

// ── Reproducir ────────────────────────────────────────────────
function reproducirCancion(urlAudio, titulo, artista, urlPortada, pk) {
    audio.src = urlAudio;
    reproductorTitulo.textContent = titulo;
    reproductorArtista.textContent = artista;
    reproduccionContada = false;

    if (urlPortada) {
        reproductorPortada.src = urlPortada;
        reproductorPortada.classList.remove('oculto');
    } else {
        reproductorPortada.classList.add('oculto');
    }

    audio.play().then(() => mostrarPausa()).catch(console.error);

    // Guardar pk actual en el elemento audio para usarlo en timeupdate
    audio.dataset.pk = pk || '';
}

function reproducirCancionConCola(urlAudio, titulo, artista, urlPortada, pk, cola) {
    if (cola && cola.length > 0) {
        colaActual = cola;
        indiceActual = cola.findIndex(c => c.pk === pk);
    }
    reproducirCancion(urlAudio, titulo, artista, urlPortada, pk);
}

// ── Play / Pausa ──────────────────────────────────────────────
btnPlayPausa.addEventListener('click', () => {
    if (!audio.src) return;
    if (audio.paused) { audio.play(); mostrarPausa(); }
    else { audio.pause(); mostrarPlay(); }
});

// ── Progreso ──────────────────────────────────────────────────
let arrastrando = false;
barraProgreso.addEventListener('mousedown', () => { arrastrando = true; });
barraProgreso.addEventListener('input', () => {
    if (audio.duration) {
        tiempoActual.textContent = formatearTiempo((barraProgreso.value / 100) * audio.duration);
    }
});
barraProgreso.addEventListener('change', () => {
    if (audio.duration) audio.currentTime = (barraProgreso.value / 100) * audio.duration;
    arrastrando = false;
});

// ── TimeUpdate — progreso + contar reproducción ───────────────
audio.addEventListener('timeupdate', () => {
    if (!arrastrando && audio.duration) {
        barraProgreso.value = (audio.currentTime / audio.duration) * 100;
        tiempoActual.textContent = formatearTiempo(audio.currentTime);
        tiempoTotal.textContent = formatearTiempo(audio.duration);
    }

    // Contar reproducción a los 30s o al 50% si dura menos de 60s
    if (!reproduccionContada && audio.duration) {
        const umbral = audio.duration < 60 ? audio.duration * 0.5 : 30;
        if (audio.currentTime >= umbral) {
            reproduccionContada = true;
            const pk = audio.dataset.pk;
            console.log('Contando reproducción, pk:', pk);
            if (pk) {
                fetch(`/cancion/${pk}/reproduccion/`, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': obtenerCsrf() }
                })
                .then(r => r.json())
                .then(data => {
                    console.log('Respuesta reproducción:', data);
                    const el = document.getElementById('contador-reproducciones');
                    if (el && data.reproducciones !== undefined) {
                        el.textContent = data.reproducciones + ' reproducciones';
                    }
                })
                .catch(err => console.error('Error fetch reproducción:', err));
            }
        }
    }
});

// ── Volumen ───────────────────────────────────────────────────
barraVolumen.addEventListener('input', () => {
    audio.volume = barraVolumen.value / 100;
    sessionStorage.setItem('volumen', barraVolumen.value);
});

// ── Anterior / Siguiente ──────────────────────────────────────
btnAnterior.addEventListener('click', () => {
    if (audio.currentTime > 3) { audio.currentTime = 0; return; }
    if (indiceActual > 0) {
        indiceActual--;
        const c = colaActual[indiceActual];
        reproducirCancion(c.url, c.titulo, c.artista, c.portada || '', c.pk);
    } else {
        audio.currentTime = 0;
    }
});

btnSiguiente.addEventListener('click', () => {
    if (indiceActual < colaActual.length - 1) {
        indiceActual++;
        const c = colaActual[indiceActual];
        reproducirCancion(c.url, c.titulo, c.artista, c.portada || '', c.pk);
    }
});

// ── Final canción → siguiente automático ─────────────────────
audio.addEventListener('ended', () => {
    mostrarPlay();
    barraProgreso.value = 0;
    tiempoActual.textContent = '0:00';
    if (indiceActual < colaActual.length - 1) {
        indiceActual++;
        const c = colaActual[indiceActual];
        reproducirCancion(c.url, c.titulo, c.artista, c.portada || '', c.pk);
    }
});

// ── Persistir estado entre páginas ───────────────────────────
function guardarEstado() {
    if (!audio.src || audio.src === window.location.href) return;
    sessionStorage.setItem('repro_src', audio.src);
    sessionStorage.setItem('repro_titulo', reproductorTitulo.textContent);
    sessionStorage.setItem('repro_artista', reproductorArtista.textContent);
    sessionStorage.setItem('repro_portada', reproductorPortada.src || '');
    sessionStorage.setItem('repro_tiempo', audio.currentTime);
    sessionStorage.setItem('repro_pk', audio.dataset.pk || '');
    sessionStorage.setItem('repro_cola', JSON.stringify(colaActual));
    sessionStorage.setItem('repro_indice', indiceActual);
    sessionStorage.setItem('repro_pausado', audio.paused ? '1' : '0');
}

function restaurarEstado() {
    const src = sessionStorage.getItem('repro_src');
    if (!src) return;

    audio.src = src;
    audio.currentTime = parseFloat(sessionStorage.getItem('repro_tiempo') || 0);
    audio.dataset.pk = sessionStorage.getItem('repro_pk') || '';
    reproductorTitulo.textContent = sessionStorage.getItem('repro_titulo') || 'Ninguna canción seleccionada';
    reproductorArtista.textContent = sessionStorage.getItem('repro_artista') || '';

    const portada = sessionStorage.getItem('repro_portada');
    if (portada && portada !== window.location.href) {
        reproductorPortada.src = portada;
        reproductorPortada.classList.remove('oculto');
    }

    const cola = sessionStorage.getItem('repro_cola');
    if (cola) {
        colaActual = JSON.parse(cola);
        indiceActual = parseInt(sessionStorage.getItem('repro_indice') || -1);
    }

    const pausado = sessionStorage.getItem('repro_pausado');
    if (pausado === '0') {
        audio.play().then(() => mostrarPausa()).catch(() => {});
    } else {
        mostrarPlay();
        tiempoTotal.textContent = formatearTiempo(audio.duration);
    }
}

// Guardar antes de salir de la página
window.addEventListener('beforeunload', guardarEstado);

// Restaurar al cargar
document.addEventListener('DOMContentLoaded', restaurarEstado);