import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import SalaChat, Mensaje
from users.models import Usuario



class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.sala_id = self.scope['url_route']['kwargs']['sala_id']
        self.grupo = f'chat_{self.sala_id}'
        self.usuario = self.scope['user']

        if not self.usuario.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.grupo, self.channel_name)
        await self.accept()

        # Enviar historial de mensajes al conectar
        mensajes = await self.obtener_historial()
        for msg in mensajes:
            await self.send(text_data=json.dumps(msg))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.grupo, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        contenido = data.get('mensaje', '').strip()
        if not contenido:
            return
        mensaje = await self.guardar_mensaje(contenido)
        await self.channel_layer.group_send(self.grupo, {
            'type': 'chat_mensaje',
            'mensaje': contenido,
            'usuario': self.usuario.username,
            'foto': mensaje['foto'],
            'enviado_en': mensaje['enviado_en'],
            'sala_id': self.sala_id,
        })

    async def chat_mensaje(self, event):
        # Marcar leído si este consumer es del receptor (no del autor)
        if event['usuario'] != self.usuario.username:
            await self.marcar_leidos()

        no_leidos = await self.contar_no_leidos_global()

        await self.send(text_data=json.dumps({
            'mensaje': event['mensaje'],
            'usuario': event['usuario'],
            'foto': event['foto'],
            'enviado_en': event['enviado_en'],
            'no_leidos_global': no_leidos,
            'sala_id': int(event['sala_id']),
        }))

    @database_sync_to_async
    def obtener_historial(self):
        sala = SalaChat.objects.get(pk=self.sala_id)
        mensajes = sala.mensajes.select_related('autor').order_by('enviado_en')[:50]
        resultado = []
        for m in mensajes:
            foto = m.autor.foto_perfil.url if m.autor.foto_perfil else ''
            resultado.append({
                'mensaje': m.contenido,
                'usuario': m.autor.username,
                'foto': foto,
                'enviado_en': m.enviado_en.strftime('%H:%M'),
            })
        return resultado

    @database_sync_to_async
    def guardar_mensaje(self, contenido):
        sala = SalaChat.objects.get(pk=self.sala_id)
        m = Mensaje.objects.create(sala=sala, autor=self.usuario, contenido=contenido)
        foto = self.usuario.foto_perfil.url if self.usuario.foto_perfil else ''
        return {
            'foto': foto,
            'enviado_en': m.enviado_en.strftime('%H:%M'),
            'mensaje_id': m.pk,
        }
        
    @database_sync_to_async
    def marcar_leidos(self):
        sala = SalaChat.objects.get(pk=self.sala_id)
        sala.mensajes.filter(leido=False).exclude(autor=self.usuario).update(leido=True)

    @database_sync_to_async
    def contar_no_leidos_global(self):
        """Cuenta no leídos totales del usuario para el badge del sidebar"""
        total = 0
        for sala in SalaChat.objects.filter(participantes=self.usuario):
            total += sala.mensajes_no_leidos(self.usuario)
        return total