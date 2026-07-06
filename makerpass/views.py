#Django imports
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
# App imports
from autenticacao.models import Servidor
from .models import Ponto
from .utils import calcular_total_horas
from .services import registrar_novo_ponto, calcular_horas_se_saida, RegraDePontoException, calcula_intervalo_de_tempo, deletar_ponto_pendente

class PaginaRegistroPontoView(View):
    template_name = "makerpass/registrar_ponto.html"
    def get(self, request, **kwargs):
        return render(request, self.template_name)
    def post(self, request, **kwargs):
	matricula = request.POST.get("matricula")
	ponto_criado, servidor = registrar_novo_ponto(matricula)
	request.session.pop("horas_trabalhadas_dia", None)
	horas_trabalhadas = calcular_horas_se_saida(ponto_criado, servidor)
	if horas_trabalhadas:
                request.session["horas_trabalhadas_dia"] = horas_trabalhadas
	return redirect("pagina_sucesso_ponto")

class PaginaSucessoPontoView(TemplateView):
    template_name = "makerpass/sucesso_ponto.html"

    def get_context_data(self, **kwargs):
        ultimo_ponto = Ponto.objects.all().last()

        context = super().get_context_data(**kwargs)
        context["ultimo_ponto"] = ultimo_ponto
        context["horas_trabalhadas_dia"] = self.request.session.pop(
            "horas_trabalhadas_dia", None
        )

        return context


def sucesso_ponto(request, ponto_criado, servidor):
    # Limpa dados antigos da sessão para garantir consistência
    request.session.pop("horas_trabalhadas_dia", None)

    # Se for um ponto de SAÍDA, calcula as horas e salva na sessão
    if not ponto_criado.eh_entrada:
        hoje = timezone.localtime(ponto_criado.data_hora_do_ponto).date()
        inicio_do_dia = timezone.make_aware(datetime.combine(hoje, time.min))
        fim_do_dia = timezone.make_aware(datetime.combine(hoje, time.max))

        pontos_do_dia = Ponto.objects.filter(
            bolsista=servidor,
            data_hora_do_ponto__gte=inicio_do_dia,
            data_hora_do_ponto__lte=fim_do_dia,
        ).order_by("data_hora_do_ponto")

        horas, minutos = calcular_total_horas(pontos_do_dia)
        horas_trabalhadas_str = f"{horas}h {minutos}min"

        # Armazena os dados na sessão para a próxima página
        request.session["horas_trabalhadas_dia"] = horas_trabalhadas_str
