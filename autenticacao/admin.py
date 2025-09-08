#DJANGO 
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, FileResponse
from django.utils import timezone
from django.utils.http import urlencode
from django.urls import reverse
from django.conf import settings
#REPORTLAB 
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
#PYTHON LIBS
import io
import os
from datetime import timedelta
#APP
from .models import User, Visitante, Servidor
from makerpass.models import Ponto
from .forms import MonthSelectorForm  


def _gerar_e_enviar_pdf(servidor, mes, ano):
    """
    Função auxiliar que contém a lógica de criação do PDF.
    Recebe o servidor, mês e ano para filtrar os pontos.
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # --- 1. CABEÇALHO --- (Seu código original, sem alterações)
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'teste_logo.png')
    try:
        if os.path.exists(logo_path):
            image_width = 4 * inch
            x_centered = (width - image_width) / 2
            p.drawImage(logo_path, x_centered , height - 2.45 * inch, width=image_width, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        print(f"ERRO CRÍTICO AO PROCESSAR IMAGEM: {e}")
    
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2.0, height - 1.75 * inch, "Relatório de Frequência do Bolsista")
    p.setFont("Helvetica", 10)
    p.drawString(inch, height - 2.2 * inch, f"Nome: {servidor.user.get_full_name() or 'Não informado'}")
    p.drawString(inch, height - 2.4 * inch, f"Matrícula: {servidor.matricula}")
    p.drawString(inch, height - 2.6 * inch, f"Período de Referência: {mes:02d}/{ano}")
    p.line(inch, height - 2.8 * inch, width - inch, height - 2.8 * inch)

    # --- 2. LÓGICA DE CÁLCULO DE HORAS (AGORA FILTRADA) ---
    # AQUI ESTÁ A MUDANÇA PRINCIPAL: filtramos por ano e mês!
    pontos_para_calculo = Ponto.objects.filter(
        bolsista=servidor, 
        data_hora_do_ponto__year=ano,
        data_hora_do_ponto__month=mes
    ).order_by('data_hora_do_ponto')
    
    total_duration = timedelta()
    entrada_time = None
    for ponto in pontos_para_calculo:
        if ponto.eh_entrada:
            entrada_time = ponto.data_hora_do_ponto
        elif not ponto.eh_entrada and entrada_time:
            duration = ponto.data_hora_do_ponto - entrada_time
            total_duration += duration
            entrada_time = None

    total_seconds = int(total_duration.total_seconds())
    total_horas = total_seconds // 3600
    total_minutos = (total_seconds % 3600) // 60

    # --- 3. TABELA DE PONTOS (AGORA FILTRADA) ---
    y_position = height - 3.2 * inch
    p.setFont("Helvetica-Bold", 12)
    p.drawString(inch, y_position, "Registros de Ponto")
    y_position -= 0.3 * inch

    # Usamos o mesmo QuerySet já filtrado
    pontos_para_display = pontos_para_calculo.order_by('-data_hora_do_ponto')
    
    # (O resto do seu código da tabela de pontos e rodapé continua aqui, sem alterações)
    if not pontos_para_display:
        p.setFont("Helvetica-Oblique", 10)
        p.drawString(inch, y_position, "Nenhum ponto registrado para este período.")
    else:
        current_day = None
        p.setFont("Helvetica-Bold", 10)
        p.drawString(inch, y_position, "Data")
        p.drawString(inch * 3, y_position, "Hora")
        p.drawString(inch * 5, y_position, "Tipo")
        y_position -= 0.3 * inch

        for ponto in pontos_para_display:
            # ... (seu código de loop for continua idêntico) ...
            hora_local = timezone.localtime(ponto.data_hora_do_ponto)
            if hora_local.date() != current_day:
                if current_day is not None:
                    y_position -= 0.1 * inch
                    p.line(inch, y_position, width - inch, y_position)
                    y_position -= 0.2 * inch
                current_day = hora_local.date()
            data_str, hora_str = hora_local.strftime("%d/%m/%Y"), hora_local.strftime("%H:%M:%S")
            tipo_str = "Entrada" if ponto.eh_entrada else "Saída"
            p.drawString(inch, y_position, data_str)
            p.drawString(inch * 3, y_position, hora_str)
            p.drawString(inch * 5, y_position, tipo_str)
            y_position -= 0.3 * inch
            if y_position < inch * 1.5:
                p.showPage()
                p.setFont("Helvetica-Bold", 10)
                y_position = height - inch
                p.drawString(inch, y_position, "Data")
                p.drawString(inch * 3, y_position, "Hora")
                p.drawString(inch * 5, y_position, "Tipo")
                y_position -= 0.3 * inch
            if ponto.eh_entrada and not ponto.eh_valido:
                # Mudamos a fonte e a cor para dar destaque à mensagem
                p.setFont("Helvetica-Oblique", 8)
                p.setFillColorRGB(0.8, 0, 0) # Vermelho escuro

                p.drawString(inch * 5, y_position, "Sem saída correspondente. Ponto inválido.")
                
                # Restauramos a fonte e a cor padrão para as próximas linhas
                p.setFont("Helvetica", 10)
                p.setFillColorRGB(0, 0, 0) # Preto
    # --- 4. RODAPÉ --- (Seu código original, sem alterações)
    p.line(inch, y_position, width - inch, y_position)
    y_position -= 0.3 * inch
    p.setFont("Helvetica-Bold", 12)
    p.drawRightString(width - inch, y_position, f"Total de Horas Trabalhadas: {total_horas}h {total_minutos}min")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    
    return FileResponse(buffer, as_attachment=True, filename=f'relatorio_pontos_{servidor.matricula}_{ano}_{mes:02d}.pdf')


# ------------------------------------------------------------------
# CLASSE ADMIN PERSONALIZADA PARA O SERVIDOR
# ------------------------------------------------------------------
class ServidorAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'get_user_email', 'get_user_first_name', 'get_user_last_name')
    search_fields = ('matricula', 'user__email', 'user__first_name', 'user__last_name')
    
    actions = ['gerar_relatorio_pontos_action']

    # ----- NOVOS MÉTODOS PARA A VIEW INTERMEDIÁRIA -----
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'gerar-relatorio/',
                self.admin_site.admin_view(self.gerar_relatorio_view),
                name='gerar_relatorio_servidor',
            )
        ]
        return custom_urls + urls

    def gerar_relatorio_view(self, request):
        context = dict(
           self.admin_site.each_context(request),
        )
        
        if request.method == 'POST':
            form = MonthSelectorForm(request.POST)
            if form.is_valid():
                servidor_id = request.POST.get('servidor_id')
                servidor = get_object_or_404(Servidor, pk=servidor_id)
                mes = int(form.cleaned_data['mes'])
                ano = int(form.cleaned_data['ano'])
                
                # Chama a função que realmente gera o PDF
                return _gerar_e_enviar_pdf(servidor, mes, ano)
        else:
            servidor_id = request.GET.get('servidor_id')
            servidor = get_object_or_404(Servidor, pk=servidor_id)
            form = MonthSelectorForm()

        context['form'] = form
        context['servidor'] = servidor
        return render(request, 'admin/gerar_relatorio.html', context)
    
    # ----- ACTION MODIFICADA -----
    @admin.action(description="Gerar Relatório de Pontos (PDF)")
    def gerar_relatorio_pontos_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Por favor, selecione apenas um bolsista para gerar o relatório.", level='error')
            return
        
        servidor_selecionado = queryset.first()
        
        # Constrói a URL para a nossa view intermediária
        base_url = reverse('admin:gerar_relatorio_servidor')
        query_string = urlencode({'servidor_id': servidor_selecionado.id})
        url = f'{base_url}?{query_string}'
        
        # Redireciona o usuário para a página de seleção de mês
        return HttpResponseRedirect(url)
    
    # Funções para display (seu código original, sem alterações)
    @admin.display(description='Email', ordering='user__email')
    def get_user_email(self, obj):
        return obj.user.email

    @admin.display(description='Nome', ordering='user__first_name')
    def get_user_first_name(self, obj):
        return obj.user.first_name

    @admin.display(description='Sobrenome', ordering='user__last_name')
    def get_user_last_name(self, obj):
        return obj.user.last_name

# REGISTRO FINAL DOS MODELS
admin.site.register(User)
admin.site.register(Visitante)
admin.site.register(Servidor, ServidorAdmin)