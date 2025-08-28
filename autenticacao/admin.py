# autenticacao/admin.py

from django.contrib import admin
from .models import User, Visitante, Servidor
from makerpass.models import Ponto

# IMPORTS PARA GERAÇÃO DE PDF
from django.http import FileResponse
from django.utils import timezone
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import os
from django.conf import settings
from datetime import timedelta


def gerar_relatorio_pontos_pdf(modeladmin, request, queryset):
    if queryset.count() != 1:
        modeladmin.message_user(request, "Por favor, selecione apenas um bolsista para gerar o relatório.", level='error')
        return

    servidor = queryset.first()
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # --- 1. CABEÇALHO COM LOGOMARCA CENTRALIZADA ---
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'teste_logo.png')
    
    try:
        if os.path.exists(logo_path):
            # Calcula a posição X para centralizar a imagem de 1 polegada de largura
            image_width = 4 * inch
            x_centered = (width - image_width) / 2
            
            # Desenha a imagem centralizada. Note que o parâmetro 'mask' foi removido,
            # pois não é necessário e pode causar problemas com arquivos JPG.
            p.drawImage(logo_path, x_centered , height - 2.45 * inch, width=image_width, preserveAspectRatio=True, mask='auto')
        else:
            print(f"AVISO: Arquivo de logo não encontrado em {logo_path}")
    except Exception as e:
        print(f"ERRO CRÍTICO AO PROCESSAR IMAGEM: {e}")

    # Posições Y ajustadas para não sobrepor a logo
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2.0, height - 1.75 * inch, "Relatório de Frequência do Bolsista")
    p.setFont("Helvetica-Bold", 16)
    # p.drawCentredString(width / 2.0, height - 1 * inch, "CNATMAKER")
    
    p.setFont("Helvetica", 10)
    p.drawString(inch, height - 2.2 * inch, f"Nome: {servidor.user.get_full_name() or 'Não informado'}")
    p.drawString(inch, height - 2.4 * inch, f"Matrícula: {servidor.matricula}")
    
    data_emissao = timezone.localtime(timezone.now()).strftime("%d/%m/%Y às %H:%M:%S")
    p.drawString(inch, height - 2.6 * inch, f"Relatório emitido em: {data_emissao}")
    
    p.line(inch, height - 2.8 * inch, width - inch, height - 2.8 * inch)


    # --- 2. LÓGICA CORRETA DE CÁLCULO DE HORAS TOTAIS ---
    # Esta lógica já calcula corretamente o total de horas em todos os períodos.
    # Ela percorre todos os pontos em ordem, encontra um par de "entrada" e "saída",
    # soma a duração e continua procurando o próximo par.
    pontos_para_calculo = Ponto.objects.filter(bolsista=servidor).order_by('data_hora_do_ponto')
    total_duration = timedelta()
    entrada_time = None

    for ponto in pontos_para_calculo:
        if ponto.eh_entrada:
            # Se já houver uma "entrada" sem "saída", ignora (considera a mais recente)
            entrada_time = ponto.data_hora_do_ponto
        elif not ponto.eh_entrada and entrada_time:
            # Se encontrar uma "saída" e houver uma "entrada" registrada, calcula a duração.
            duration = ponto.data_hora_do_ponto - entrada_time
            total_duration += duration
            entrada_time = None # Reseta para que a próxima "saída" precise de uma nova "entrada"

    total_seconds = int(total_duration.total_seconds())
    total_horas = total_seconds // 3600
    total_minutos = (total_seconds % 3600) // 60

    # --- 3. TABELA DE PONTOS COM SEPARADOR DIÁRIO ---
    y_position = height - 3.2 * inch
    p.setFont("Helvetica-Bold", 12)
    p.drawString(inch, y_position, "Registros de Ponto")
    y_position -= 0.3 * inch
    
    pontos_para_display = Ponto.objects.filter(bolsista=servidor).order_by('-data_hora_do_ponto')
    
    if not pontos_para_display:
        p.setFont("Helvetica-Oblique", 10)
        p.drawString(inch, y_position, "Nenhum ponto registrado para este servidor.")
    else:
        current_day = None
        # Cabeçalho da tabela
        p.setFont("Helvetica-Bold", 10)
        p.drawString(inch, y_position, "Data")
        p.drawString(inch * 3, y_position, "Hora")
        p.drawString(inch * 5, y_position, "Tipo")
        y_position -= 0.3 * inch

        for ponto in pontos_para_display:
            hora_local = timezone.localtime(ponto.data_hora_do_ponto)
            
            if hora_local.date() != current_day:
                if current_day is not None:
                    y_position -= 0.1 * inch
                    p.line(inch, y_position, width - inch, y_position)
                    y_position -= 0.2 * inch
                current_day = hora_local.date()

            data_str = hora_local.strftime("%d/%m/%Y")
            hora_str = hora_local.strftime("%H:%M:%S")
            tipo_str = "Entrada" if ponto.eh_entrada else "Saída"
            
            p.setFont("Helvetica", 10)
            p.drawString(inch, y_position, data_str)
            p.drawString(inch * 3, y_position, hora_str)
            p.drawString(inch * 5, y_position, tipo_str)
            y_position -= 0.3 * inch

            if y_position < inch * 1.5:
                p.showPage()
                # Redesenha o cabeçalho na nova página, se desejar
                p.setFont("Helvetica-Bold", 10)
                y_position = height - inch
                p.drawString(inch, y_position, "Data")
                p.drawString(inch * 3, y_position, "Hora")
                p.drawString(inch * 5, y_position, "Tipo")
                y_position -= 0.3 * inch

    # --- 4. RODAPÉ COM TOTAL DE HORAS ---
    p.line(inch, y_position, width - inch, y_position)
    y_position -= 0.3 * inch
    p.setFont("Helvetica-Bold", 12)
    p.drawRightString(width - inch, y_position, f"Total de Horas Trabalhadas: {total_horas}h {total_minutos}min")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    
    return FileResponse(buffer, as_attachment=True, filename=f'relatorio_pontos_{servidor.matricula}.pdf')


gerar_relatorio_pontos_pdf.short_description = "Gerar Relatório de Pontos (PDF)"


# ------------------------------------------------------------------
# CLASSE ADMIN PERSONALIZADA PARA O SERVIDOR
# ------------------------------------------------------------------
class ServidorAdmin(admin.ModelAdmin):
    # CORREÇÃO: Usamos o '__' para acessar campos do modelo 'user' relacionado.
    list_display = ('matricula', 'get_user_email', 'get_user_first_name', 'get_user_last_name')
    search_fields = ('matricula', 'user__email', 'user__first_name', 'user__last_name')
    
    actions = [gerar_relatorio_pontos_pdf]

    # Funções para tornar os campos relacionados mais amigáveis no admin
    @admin.display(description='Email', ordering='user__email')
    def get_user_email(self, obj):
        return obj.user.email

    @admin.display(description='Nome', ordering='user__first_name')
    def get_user_first_name(self, obj):
        return obj.user.first_name

    @admin.display(description='Sobrenome', ordering='user__last_name')
    def get_user_last_name(self, obj):
        return obj.user.last_name

# ------------------------------------------------------------------
# REGISTRO FINAL DOS MODELS
# ------------------------------------------------------------------
admin.site.register(User)
admin.site.register(Visitante)
admin.site.register(Servidor, ServidorAdmin)