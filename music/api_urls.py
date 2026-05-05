from rest_framework.routers import DefaultRouter
from .api_views import CancionViewSet, PlaylistViewSet, UsuarioViewSet

router = DefaultRouter()
router.register(r'canciones', CancionViewSet, basename='cancion-api')
router.register(r'playlists', PlaylistViewSet, basename='playlist-api')
router.register(r'usuarios', UsuarioViewSet, basename='usuario-api')

urlpatterns = router.urls