#PYTHON IMPORTS
import json
from datetime import timedelta, datetime, time
#DJANGO IMPORTS
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView
from django.views import View
from django.contrib import messages
from django.utils import timezone
#APP IMPORTS
from .models import *
from autenticacao.models import Servidor, User 

class PaginaRegistroPontoView(View):
    template_name = 'makerpass/registrar_ponto.html'

    def get(self, request, **kwargs):
        return render(request, self.template_name)
    
    def post(self, request, **kwargs):
        matricula = request.POST.get('matricula')
        if not matricula:
            messages.error(request, "Matrícula não informada.")
            return redirect('pagina_registro_ponto')
        try:
            servidor = Servidor.objects.get(matricula=matricula)
        except Servidor.DoesNotExist:
            messages.error(request, "Bolsista não encontrado.")
            return redirect('pagina_registro_ponto')
        
        #--- INTEVALO DE 1 MIN. PARA REGISTRO DE PONTO ---
        ultimo_ponto = Ponto.objects.filter(bolsista=servidor).last()
        agora = timezone.now()

        if ultimo_ponto:
            tempo_desde_ultimo_ponto = agora - ultimo_ponto.data_hora_do_ponto
            if tempo_desde_ultimo_ponto < timedelta(minutes=1):
                segundos_restantes = int(60 - tempo_desde_ultimo_ponto.total_seconds())
                messages.error(request, f"Aguarde {segundos_restantes} segundos para registrar um novo ponto.")
                return redirect('pagina_registro_ponto')


        #--- LÓGICA PARA DELETAR PONTOS PENDENTES DO DIA ANTERIOR ---
        eh_entrada = not ultimo_ponto.eh_entrada if ultimo_ponto else True
        
        if not eh_entrada:
            if ultimo_ponto.data_hora_do_ponto.date() < timezone.now().date():
                ultimo_ponto.delete()
                eh_entrada = True

        ponto_criado = Ponto.objects.create(bolsista=servidor, eh_entrada=eh_entrada)

        #--- ENVIA DADOS PARA A PÁGINA DE SUCESSO ATRAVÉS DA SESSAO ---
        sucesso_ponto(request, ponto_criado, servidor)
        
        return redirect('pagina_sucesso_ponto')

class PaginaSucessoPontoView(TemplateView):
    template_name = 'makerpass/sucesso_ponto.html'
    
    def get_context_data(self, **kwargs):
        ultimo_ponto = Ponto.objects.all().last()
        
        context = super().get_context_data(**kwargs)
        context['ultimo_ponto'] = ultimo_ponto
        context['horas_trabalhadas_dia'] = self.request.session.pop('horas_trabalhadas_dia', None)
        
        return context

def sucesso_ponto(request, ponto_criado, servidor):
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
