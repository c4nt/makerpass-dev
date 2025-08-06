#PYTHON IMPORTS
import json
import asyncio
from datetime import timedelta, datetime, time
#DJANGO IMPORTS
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
#APP IMPORTS
from .models import *
from autenticacao.models import Servidor, User 

class PaginaRegistroPontoView(View):
    template_name = 'makerpass/registrar_ponto.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        matricula = request.POST.get('matricula')
        if not matricula:
            messages.error(request, "Matrícula não informada.")
            return redirect('pagina_registro_ponto')

        try:
            servidor = Servidor.objects.get(matricula=matricula)
        except Servidor.DoesNotExist:
            messages.error(request, "Bolsista não encontrado.")
            return redirect('pagina_registro_ponto')

        ultimo_ponto = Ponto.objects.filter(bolsista=servidor).last()
        agora = timezone.now()

        if ultimo_ponto:
            tempo_desde_ultimo_ponto = agora - ultimo_ponto.data_hora_do_ponto
            if tempo_desde_ultimo_ponto < timedelta(minutes=1):
                segundos_restantes = int(60 - tempo_desde_ultimo_ponto.total_seconds())
                messages.error(request, f"Aguarde {segundos_restantes} segundos para registrar um novo ponto.")
                return redirect('pagina_registro_ponto')

        eh_entrada = not ultimo_ponto.eh_entrada if ultimo_ponto else True
        ponto_criado = Ponto.objects.create(bolsista=servidor, eh_entrada=eh_entrada)

        # --- LÓGICA DE SUCESSO COM SESSÃO ---
        # Limpa dados antigos da sessão para garantir consistência
        request.session.pop('horas_trabalhadas_dia', None)

        # Se for um ponto de SAÍDA, calcula as horas e salva na sessão
        if not ponto_criado.eh_entrada:
            hoje = timezone.localtime(ponto_criado.data_hora_do_ponto).date()
            inicio_do_dia = timezone.make_aware(datetime.combine(hoje, time.min))
            fim_do_dia = timezone.make_aware(datetime.combine(hoje, time.max))
            
            pontos_do_dia = Ponto.objects.filter(
                bolsista=servidor, data_hora_do_ponto__gte=inicio_do_dia, data_hora_do_ponto__lte=fim_do_dia
            ).order_by('data_hora_do_ponto')

            total_duration = timedelta()
            entrada_time = None
            for ponto in pontos_do_dia:
                if ponto.eh_entrada:
                    entrada_time = ponto.data_hora_do_ponto
                elif not ponto.eh_entrada and entrada_time:
                    duration = ponto.data_hora_do_ponto - entrada_time
                    total_duration += duration
                    entrada_time = None
            
            horas = int(total_duration.total_seconds()) // 3600
            minutos = (int(total_duration.total_seconds()) % 3600) // 60
            horas_trabalhadas_str = f"{horas}h {minutos}min"
            
            # Armazena os dados na sessão para a próxima página
            request.session['horas_trabalhadas_dia'] = horas_trabalhadas_str
        
        # --- FIM DA LÓGICA DE SUCESSO COM SESSÃO ---  

        ordem_para_arduino = "ABRIR" if eh_entrada else None
        
        return redirect('pagina_sucesso_ponto')

class PaginaSucessoPontoView(TemplateView):
    template_name = 'makerpass/sucesso_ponto.html'
    
    def get_context_data(self, **kwargs):
        ultimo_ponto = Ponto.objects.all().last()
        
        context = super().get_context_data(**kwargs)
        context['ultimo_ponto'] = ultimo_ponto
        context['horas_trabalhadas_dia'] = self.request.session.pop('horas_trabalhadas_dia', None)
        
        return context
    
@method_decorator(csrf_exempt, name='dispatch')
class ApiRegistrarPontoView(View):

    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            id_sensor = data['id_sensor']
            print(id)

            # A lógica de negócio principal é exatamente a mesma.
            servidor = await Servidor.objects.aget(id_sensor_biometrico=id_sensor)
            ultimo_ponto = await Ponto.objects.filter(bolsista=servidor).alast()

            if ultimo_ponto:
                agora = timezone.now()
                tempo_desde_ultimo_ponto = agora - ultimo_ponto.data_hora_do_ponto

                if tempo_desde_ultimo_ponto < timedelta(minutes=1):
                    segundos_restantes = int(60 - tempo_desde_ultimo_ponto.total_seconds())
                    print(f"[API] Registro bloqueado para {servidor.matricula}. Tolerância de 1 min. Faltam {segundos_restantes}s.")
                    
                    return JsonResponse({
                        "status": "error",
                        "message": f"Aguarde {segundos_restantes} segundos para registrar um novo ponto."
                    }, status=429)

            eh_entrada = not ultimo_ponto.eh_entrada if ultimo_ponto else True

            ponto_criado = await Ponto.objects.acreate(bolsista=servidor, eh_entrada=eh_entrada)
            print(ponto_criado)

            ordem_para_arduino = "ABRIR" if eh_entrada else None

            
            # TODO: Notificar o stream de eventos sobre o 'ponto_criado'.
            # (Nosso próximo passo!)

            return JsonResponse({
                "status": "success",
                "message": "Ponto registrado com sucesso.",
                "servidor": servidor.matricula,
                "tipo_registro": "Entrada" if eh_entrada else "Saída",
                "ordem":ordem_para_arduino
            })
        except Servidor.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Matrícula não encontrada."}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    async def get(self, request, *args, **kwargs):
        # É uma boa prática responder a métodos não permitidos.
        return JsonResponse({"status": "error", "message": "Método GET não permitido."}, status=405)

class PontoStreamEventsView(View):
    """
    Esta classe lida com a conexão de Streaming para o frontend.
    A lógica agora está dentro do método 'get'.
    """
    async def get(self, request, *args, **kwargs):
        async def event_stream():
            # A lógica de notificação virá aqui.
            # Por enquanto, a view está pronta para recebê-la.
            while True:
                # TODO: Implementar a lógica para esperar por uma notificação
                # da ApiRegistrarPontoView.
                await asyncio.sleep(1)

        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


# class RegistroPonto(View):
    
#     async def post(self, request, *args, **kwargs):
        
#         print(request.POST['matricula'])
#         bolsista = Servidor.objects.get(matricula=request.POST['matricula'])
#         prox_tipo_eh_entrada = True

#         if Ponto.objects.filter(bolsista=bolsista):
#             if Ponto.objects.filter(bolsista=bolsista).latest('data_hora_do_ponto').eh_entrada == True:
#                 prox_tipo_eh_entrada = False
#             else:
#                 prox_tipo_eh_entrada = True
        

#         novo_ponto = Ponto.objects.create(
#             bolsista=bolsista,
#             eh_entrada=prox_tipo_eh_entrada
#         )

#         hora_local = timezone.localtime(novo_ponto.data_hora_do_ponto)
#         hora_formatada = hora_local.strftime('%H:%M')


#         tipo_acao = "Entrada" if novo_ponto.eh_entrada else "Saída"
#         messages.success(request, f"{tipo_acao} registrada com sucesso ás {hora_formatada}!")

#         return redirect('registrar_ponto')

#     async def get(self, request, *args, **kwargs):
#         async def event_stream():
#             async for novo_dado in monitora_arquivo_json():
#                 formatted_data = f"data: {json.dumps(novo_dado)}\n\n"
#                 yield formatted_data.encode('utf-8')
        
#         response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
#         response['Cache-Control'] = 'no-cache'
#         return response


#         return render(request, 'makerpass/registrar_ponto.html')


