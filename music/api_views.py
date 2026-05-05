from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Cancion, Playlist
from users.models import Usuario
from .serializers import CancionSerializer, PlaylistSerializer, UsuarioSerializer


class PaginacionEstandar(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limite'
    max_page_size = 50


class EsPropietarioOSoloLectura(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        propietario = getattr(obj, 'artista', None) or getattr(obj, 'propietario', None)
        return propietario == request.user


class CancionViewSet(viewsets.ModelViewSet):
    serializer_class = CancionSerializer
    permission_classes = [permissions.IsAuthenticated, EsPropietarioOSoloLectura]
    pagination_class = PaginacionEstandar
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titulo', 'artista__username']
    ordering_fields = ['fecha_subida', 'reproducciones', 'titulo']
    ordering = ['-fecha_subida']

    def get_queryset(self):
        return Cancion.objects.filter(es_publica=True).select_related('artista')

    def perform_create(self, serializer):
        serializer.save(artista=self.request.user)

    @action(detail=False, methods=['get'])
    def mis_canciones(self, request):
        canciones = Cancion.objects.filter(artista=request.user)
        serializer = self.get_serializer(canciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def populares(self, request):
        canciones = Cancion.objects.filter(es_publica=True).order_by('-reproducciones')[:10]
        serializer = self.get_serializer(canciones, many=True)
        return Response(serializer.data)


class PlaylistViewSet(viewsets.ModelViewSet):
    serializer_class = PlaylistSerializer
    permission_classes = [permissions.IsAuthenticated, EsPropietarioOSoloLectura]
    pagination_class = PaginacionEstandar
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'propietario__username']

    def get_queryset(self):
        return Playlist.objects.filter(es_publica=True).select_related('propietario')

    def perform_create(self, serializer):
        serializer.save(propietario=self.request.user)

    @action(detail=False, methods=['get'])
    def mis_playlists(self, request):
        playlists = Playlist.objects.filter(propietario=request.user)
        serializer = self.get_serializer(playlists, many=True)
        return Response(serializer.data)


class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']

    @action(detail=False, methods=['get'])
    def yo(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)