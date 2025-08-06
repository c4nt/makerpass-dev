from django.urls import path
from .views import *

# Optar por utilizar CBV ao invés de FBV
urlpatterns = [
    path('', PaginaRegistroPontoView.as_view(), name='pagina_registro_ponto'),
    path('sucesso/', PaginaSucessoPontoView.as_view(), name='pagina_sucesso_ponto'),
    # path('api/registrar/', ApiRegistrarPontoView.as_view(), name='api_registrar_ponto'),
    # path('events/stream/', PontoStreamEventsView.as_view(), name='ponto_stream_events'),
] 
