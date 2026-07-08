from datetime import timedelta, time, datetime
from django.utils import timezone
from autenticacao.models import Servidor
from .models import Ponto
from .utils import calcular_total_horas

class RegraDePontoException(Exception):
    pass

def get_data(request):
	matricula = request.POST.get("matricula")
	if not matricula:
	        raise RegraDePontoException("Matricula não informada.")
    	try:
        	servidor = Servidor.objects.get(matricula=matricula)
    	except Servidor.DoesNotExist:
        	raise RegraDePontoException("Bolsista não encontrado.")
	servidor = Servidor.objects.get(matricula=matricula)
        ultimo_ponto = Ponto.objects.filter(bolsista=servidor).last()
	return servidor, ultimo_ponto

def registrar_novo_ponto(servidor, ultimo_ponto):
    _entrada = not ultimo_ponto.eh_entrada if ultimo_ponto else True
    ponto_criado = Ponto.objects.create(bolsista=servidor, eh_entrada=eh_entrada)
    return ponto_criado

def calcula_intervalo_de_tempo(ultimo_ponto):
    agora = timezone.now()
    if ultimo_ponto:
	tempo_desde_ultimo_ponto = agora - ultimo_ponto.data_hora_do_ponto
    if tempo_desde_ultimo_ponto < timedelta(minutes=1):
	 segundos_restantes = int(60 - tempo_desde_ultimo_ponto.total_seconds())
    raise RegraDePontoException(
                f"Aguarde {segundos_restantes} segundos para registrar um novo ponto."
            )

def deletar_ponto_pendente(ultimo_ponto):
    agora = timezone.now()
    not eh_entrada:
	if ultimo_ponto.data_hora_do_ponto.date() < agora.date()
		ultimo_ponto.delete()
		eh_entrada = True

def calcular_horas_se_saida(ponto_criado, servidor):
    if ponto_criado.eh_entrada:
        return None
    hoje = timezone.localtime(ponto_criado.data_hora_do_ponto).date()
    inicio_do_dia = timezone.make_aware(datetime.combine(hoje, time.min))
    fim_do_dia = timezone.make_aware(datetime.combine(hoje, time.max))
    pontos_do_dia = Ponto.objects.filter(
        bolsista=servidor,
        data_hora_do_ponto__gte=inicio_do_dia,
        data_hora_do_ponto__lte=fim_do_dia,
    ).order_by("data_hora_do_ponto")
    horas, minutos = calcular_total_horas(pontos_do_dia)
    return f"{horas}h {minutos}min"
