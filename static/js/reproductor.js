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
const btnAleatorio = document.getElementById('btn-aleatorio');
const btnRepetir = document.getElementById('btn-repetir');
const btnMeGustaRepro = document.getElementById('btn-me-gusta-repro');

// ── Estado ────────────────────────────────────────────────────
let colaActual = [];
let indiceActual = -1;
let reproduccionContada = false;
let modoAleatorio = false;
let modoRepetir = false;
let pkActual = null;

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

// ── Me gusta en el reproductor ────────────────────────────────
function actualizarBotonMeGusta(yaGusta) {
    if (!btnMeGustaRepro) return;
    btnMeGustaRepro.textContent = yaGusta ? '♥' : '♡';
    btnMeGustaRepro.classList.toggle('activo', yaGusta);
    btnMeGustaRepro.classList.remove('oculto');
}

function toggleMeGustaRepro() {
    if (!pkActual) return;
    fetch(`/cancion/${pkActual}/me-gusta/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': obtenerCsrf() }
    })
    .then(r => r.json())
    .then(data => {
        const yaGusta = data.accion === 'añadido';
        actualizarBotonMeGusta(yaGusta);
        // Sincronizar con el botón de la página de detalle si está visible
        const btnDetalle = document.querySelector('.btn-me-gusta');
        if (btnDetalle) {
            btnDetalle.textContent = yaGusta ? '♥' : '♡';
            btnDetalle.classList.toggle('activo', yaGusta);
        }
    })
    .catch(console.error);
}

// ── Aleatorio ─────────────────────────────────────────────────
function toggleAleatorio() {
    modoAleatorio = !modoAleatorio;
    btnAleatorio.classList.toggle('activo', modoAleatorio);
    if (modoAleatorio) modoRepetir = false;
    btnRepetir.classList.toggle('activo', modoRepetir);
}

// ── Repetir ───────────────────────────────────────────────────
function toggleRepetir() {
    modoRepetir = !modoRepetir;
    btnRepetir.classList.toggle('activo', modoRepetir);
    if (modoRepetir) modoAleatorio = false;
    btnAleatorio.classList.toggle('activo', modoAleatorio);
}

// ── Reproducir ────────────────────────────────────────────────
function reproducirCancion(urlAudio, titulo, artista, urlPortada, pk) {
    audio.src = urlAudio;
    reproductorTitulo.textContent = titulo;
    reproductorArtista.textContent = artista;
    reproduccionContada = false;
    pkActual = pk || null;
    audio.dataset.pk = pkActual || '';

    if (urlPortada) {
        reproductorPortada.src = urlPortada;
        reproductorPortada.classList.remove('oculto');
    } else {
        reproductorPortada.classList.add('oculto');
    }

    audio.play().then(() => mostrarPausa()).catch(console.error);

    // Comprobar si ya tiene me gusta
    if (pkActual) {
        fetch(`/cancion/${pkActual}/me-gusta-estado/`)
            .then(r => r.json())
            .then(data => actualizarBotonMeGusta(data.ya_gusta))
            .catch(() => btnMeGustaRepro && btnMeGustaRepro.classList.remove('oculto'));
    }
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

// ── Progreso ────────────────────────────────────────────────────
let arrastrando = false;

// Ratón
barraProgreso.addEventListener('mousedown', () => { arrastrando = true; });
document.addEventListener('mouseup', () => { arrastrando = false; });

// Táctil (móvil)
barraProgreso.addEventListener('touchstart', () => { arrastrando = true; }, { passive: true });
barraProgreso.addEventListener('touchend', () => {
    if (audio.duration) {
        audio.currentTime = (barraProgreso.value / 100) * audio.duration;
    }
    arrastrando = false;
});

barraProgreso.addEventListener('input', () => {
    if (audio.duration) {
        tiempoActual.textContent = formatearTiempo((barraProgreso.value / 100) * audio.duration);
    }
});

barraProgreso.addEventListener('change', () => {
    if (audio.duration) {
        audio.currentTime = (barraProgreso.value / 100) * audio.duration;
    }
    arrastrando = false;
});

// ── TimeUpdate ────────────────────────────────────────────────
audio.addEventListener('timeupdate', () => {
    if (!arrastrando && audio.duration) {
        barraProgreso.value = (audio.currentTime / audio.duration) * 100;
        tiempoActual.textContent = formatearTiempo(audio.currentTime);
        tiempoTotal.textContent = formatearTiempo(audio.duration);
    }
    if (!reproduccionContada && audio.duration) {
        const umbral = audio.duration < 60 ? audio.duration * 0.5 : 30;
        if (audio.currentTime >= umbral) {
            reproduccionContada = true;
            const pk = audio.dataset.pk;
            if (pk) {
                fetch(`/cancion/${pk}/reproduccion/`, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': obtenerCsrf() }
                })
                .then(r => r.json())
                .then(data => {
                    const el = document.getElementById('contador-reproducciones');
                    if (el && data.reproducciones !== undefined) {
                        el.textContent = data.reproducciones + ' reproducciones';
                    }
                })
                .catch(console.error);
            }
        }
    }
});

// ── Volumen ───────────────────────────────────────────────────
barraVolumen.addEventListener('input', () => {
    audio.volume = barraVolumen.value / 100;
    sessionStorage.setItem('volumen', barraVolumen.value);
});

// ── Anterior ──────────────────────────────────────────────────
btnAnterior.addEventListener('click', () => {
    if (audio.currentTime > 3) { audio.currentTime = 0; return; }
    if (modoAleatorio && colaActual.length > 1) {
        let idx;
        do { idx = Math.floor(Math.random() * colaActual.length); } while (idx === indiceActual);
        indiceActual = idx;
    } else if (indiceActual > 0) {
        indiceActual--;
    } else {
        audio.currentTime = 0; return;
    }
    const c = colaActual[indiceActual];
    reproducirCancion(c.url, c.titulo, c.artista, c.portada || '', c.pk);
});

// ── Siguiente ─────────────────────────────────────────────────
btnSiguiente.addEventListener('click', () => {
    avanzarSiguiente();
});

function avanzarSiguiente() {
    if (colaActual.length === 0) return;
    if (modoAleatorio) {
        let idx;
        do { idx = Math.floor(Math.random() * colaActual.length); } while (idx === indiceActual && colaActual.length > 1);
        indiceActual = idx;
    } else if (indiceActual < colaActual.length - 1) {
        indiceActual++;
    } else {
        return;
    }
    const c = colaActual[indiceActual];
    reproducirCancion(c.url, c.titulo, c.artista, c.portada || '', c.pk);
}

// ── Final canción ─────────────────────────────────────────────
audio.addEventListener('ended', () => {
    mostrarPlay();
    barraProgreso.value = 0;
    tiempoActual.textContent = '0:00';

    if (modoRepetir) {
        audio.currentTime = 0;
        audio.play().then(() => mostrarPausa()).catch(console.error);
        return;
    }
    avanzarSiguiente();
});

// ── Guardar / Restaurar estado entre páginas ──────────────────
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
    sessionStorage.setItem('repro_aleatorio', modoAleatorio ? '1' : '0');
    sessionStorage.setItem('repro_repetir', modoRepetir ? '1' : '0');
}

function restaurarEstado() {
    const src = sessionStorage.getItem('repro_src');
    if (!src) return;

    audio.src = src;
    audio.currentTime = parseFloat(sessionStorage.getItem('repro_tiempo') || 0);
    pkActual = sessionStorage.getItem('repro_pk') || null;
    audio.dataset.pk = pkActual || '';
    // Restaurar enlaces
    const linkPortada = document.getElementById('reproductor-link-portada');
    const linkTitulo = document.getElementById('reproductor-link-titulo');
    const linkArtista = document.getElementById('reproductor-link-artista');
    if (linkPortada) linkPortada.href = pkActual ? `/cancion/${pkActual}/` : '#';
    if (linkTitulo) linkTitulo.href = pkActual ? `/cancion/${pkActual}/` : '#';
    const artistaGuardado = sessionStorage.getItem('repro_artista');
    if (linkArtista) linkArtista.href = artistaGuardado ? `/users/perfil/${artistaGuardado}/` : '#';

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

    modoAleatorio = sessionStorage.getItem('repro_aleatorio') === '1';
    modoRepetir = sessionStorage.getItem('repro_repetir') === '1';
    btnAleatorio.classList.toggle('activo', modoAleatorio);
    btnRepetir.classList.toggle('activo', modoRepetir);

    if (pkActual) {
        fetch(`/cancion/${pkActual}/me-gusta-estado/`)
            .then(r => r.json())
            .then(data => actualizarBotonMeGusta(data.ya_gusta))
            .catch(() => {});
    }
    
    const pausado = sessionStorage.getItem('repro_pausado');
    if (pausado === '0') {
        audio.play().then(() => mostrarPausa()).catch(() => {});
    } else {
        mostrarPlay();
    }
}

window.addEventListener('beforeunload', guardarEstado);
document.addEventListener('DOMContentLoaded', restaurarEstado);