from django.urls import path
from .views import LoginView, TipoCadastroView, CadastroVisitanteView, CadastroServidorView, CadastroSucessoView

# Optar por utilizar CBV ao invés de FBV
urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("cadastro/tipo", TipoCadastroView.as_view(), name="tipo_cadastro"),
    path(
        "cadastro/visitante", CadastroVisitanteView.as_view(), name="cadastro_visitante"
    ),
    path("cadastro/servidor", CadastroServidorView.as_view(), name="cadastro_servidor"),
    path("cadastro/sucesso/", CadastroSucessoView.as_view(), name="cadastro_sucesso"),
]
