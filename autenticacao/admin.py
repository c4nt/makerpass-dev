# pylint: disable=too-many-locals, too-many-statements, broad-exception-caught, inconsistent-return-statements, disable=unused-argument

# Standard imports
import io
import os

# Django imports
from django.conf import settings
from django.contrib import admin
from django.http import FileResponse
from django.utils import timezone

# ReportLab imports
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# Local imports
from makerpass.models import Ponto
from makerpass.utils import calcular_total_horas
from .models import Servidor, User, Visitante


# ---------------------------
# Constantes de layout
# ---------------------------
PAGE_SIZE = letter
PAGE_MARGIN = inch
TABLE_HEADER_FONT = ("Helvetica-Bold", 10)
TABLE_TEXT_FONT = ("Helvetica", 10)
TITLE_FONT = ("Helvetica-Bold", 16)
SUBTITLE_FONT = ("Helvetica-Bold", 12)
IMAGE_WIDTH_INCHES = 4  # largura da logomarca em polegadas
TITLE_Y = 1.75  # em polegadas a partir do topo
LOGO_Y = 2.45  # em polegadas a partir do topo
IDENTITY_START_Y = 2.2  # em polegadas a partir do topo
SECTION_SPACING = 0.3 * inch
DAY_SEPARATOR_SPACING = 0.1 * inch
MIN_Y_FOR_PAGE_BREAK = 1.5 * inch

COL_DATE_X = PAGE_MARGIN
COL_TIME_X = PAGE_MARGIN * 3
COL_TYPE_X = PAGE_MARGIN * 5

def check_value(val):
    if val < 0:
        ValueError("O valor deve ser positivo")

# ---------------------------
# Funções auxiliares de renderização
# ---------------------------
def _get_logo_path() -> str:
    return os.path.join(settings.BASE_DIR, "static", "images", "teste_logo.png")


def _draw_logo(pdf: canvas.Canvas, width: float, height: float) -> None:
    logo_path = _get_logo_path()
    try:
        if os.path.exists(logo_path):
            image_width = IMAGE_WIDTH_INCHES * inch
            x_centered = (width - image_width) / 2
            pdf.drawImage(
                logo_path,
                x_centered,
                height - LOGO_Y * inch,
                width=image_width,
                preserveAspectRatio=True,
            )
        else:
            print(f"AVISO: Arquivo de logo não encontrado em {logo_path}")
    except Exception as e:
        print(f"ERRO CRÍTICO AO PROCESSAR IMAGEM: {e}")


def _draw_title_and_identity(
    pdf: canvas.Canvas, width: float, height: float, servidor: Servidor
) -> None:
    pdf.setFont(*TITLE_FONT)
    pdf.drawCentredString(
        width / 2.0, height - TITLE_Y * inch, "Relatório de Frequência do Bolsista"
    )

    pdf.setFont(*TABLE_TEXT_FONT)
    pdf.drawString(
        PAGE_MARGIN,
        height - IDENTITY_START_Y * inch,
        f"Nome: {servidor.user.get_full_name() or 'Não informado'}",
    )
    pdf.drawString(
        PAGE_MARGIN, height - (IDENTITY_START_Y + 0.2) * inch, f"Matrícula: {servidor.matricula}"
    )

    data_emissao = timezone.localtime(timezone.now()).strftime("%d/%m/%Y às %H:%M:%S")
    pdf.drawString(
        PAGE_MARGIN,
        height - (IDENTITY_START_Y + 0.4) * inch,
        f"Relatório emitido em: {data_emissao}",
    )

    pdf.line(
        PAGE_MARGIN,
        height - (IDENTITY_START_Y + 0.6) * inch,
        width - PAGE_MARGIN,
        height - (IDENTITY_START_Y + 0.6) * inch,
    )


def _get_pontos_queryset(servidor: Servidor):
    pontos_para_calculo = Ponto.objects.filter(bolsista=servidor).order_by("data_hora_do_ponto")
    pontos_para_display = Ponto.objects.filter(bolsista=servidor).order_by("-data_hora_do_ponto")
    return pontos_para_calculo, pontos_para_display


def _draw_table_header(pdf: canvas.Canvas, y: float) -> float:
    pdf.setFont(*TABLE_HEADER_FONT)
    pdf.drawString(COL_DATE_X, y, "Data")
    pdf.drawString(COL_TIME_X, y, "Hora")
    pdf.drawString(COL_TYPE_X, y, "Tipo")
    return y - SECTION_SPACING


def _start_table_section(pdf: canvas.Canvas, height: float) -> float:
    pdf.setFont(*SUBTITLE_FONT)
    y = height - (IDENTITY_START_Y + 1.0) * inch
    pdf.drawString(PAGE_MARGIN, y, "Registros de Ponto")
    return y - SECTION_SPACING


def _new_page_with_table_header(pdf: canvas.Canvas, height: float) -> float:
    pdf.showPage()
    pdf.setFont(*TABLE_HEADER_FONT)
    y = height - PAGE_MARGIN
    pdf.drawString(COL_DATE_X, y, "Data")
    pdf.drawString(COL_TIME_X, y, "Hora")
    pdf.drawString(COL_TYPE_X, y, "Tipo")
    return y - SECTION_SPACING


def _draw_day_separator(pdf: canvas.Canvas, width: float, y: float) -> float:
    y -= DAY_SEPARATOR_SPACING
    pdf.line(PAGE_MARGIN, y, width - PAGE_MARGIN, y)
    return y - (DAY_SEPARATOR_SPACING + 0.1 * inch)


def _render_points_table(
    pdf: canvas.Canvas, width: float, height: float, pontos_para_display
) -> float:
    y = _start_table_section(pdf, height)

    if not pontos_para_display:
        pdf.setFont("Helvetica-Oblique", 10)
        pdf.drawString(PAGE_MARGIN, y, "Nenhum ponto registrado para este servidor.")
        return y

    y = _draw_table_header(pdf, y)
    current_day = None

    pdf.setFont(*TABLE_TEXT_FONT)

    for ponto in pontos_para_display:
        hora_local = timezone.localtime(ponto.data_hora_do_ponto)
        ponto_day = hora_local.date()

        if current_day is not None and ponto_day != current_day:
            y = _draw_day_separator(pdf, width, y)
        current_day = ponto_day

        data_str = hora_local.strftime("%d/%m/%Y")
        hora_str = hora_local.strftime("%H:%M:%S")
        tipo_str = "Entrada" if ponto.eh_entrada else "Saída"

        pdf.drawString(COL_DATE_X, y, data_str)
        pdf.drawString(COL_TIME_X, y, hora_str)
        pdf.drawString(COL_TYPE_X, y, tipo_str)
        y -= SECTION_SPACING

        if y < MIN_Y_FOR_PAGE_BREAK:
            y = _new_page_with_table_header(pdf, height)

    return y


def _draw_totals_footer(
    pdf: canvas.Canvas, width: float, y: float, total_horas: int, total_minutos: int
) -> None:
    pdf.line(PAGE_MARGIN, y, width - PAGE_MARGIN, y)
    y -= SECTION_SPACING
    pdf.setFont(*SUBTITLE_FONT)
    pdf.drawRightString(
        width - PAGE_MARGIN,
        y,
        f"Total de Horas Trabalhadas: {total_horas}h {total_minutos}min",
    )


# ---------------------------
# Ação do Admin: gerar PDF
# ---------------------------
def gerar_relatorio_pontos_pdf(modeladmin, request, queryset):
    if queryset.count() != 1:
        modeladmin.message_user(
            request,
            "Por favor, selecione apenas um bolsista para gerar o relatório.",
            level="error",
        )
        return

    servidor = queryset.first()
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=PAGE_SIZE)
    width, height = PAGE_SIZE

    _draw_logo(pdf, width, height)
    _draw_title_and_identity(pdf, width, height, servidor)

    pontos_para_calculo, pontos_para_display = _get_pontos_queryset(servidor)
    total_horas, total_minutos = calcular_total_horas(pontos_para_calculo)

    y_position = _render_points_table(pdf, width, height, pontos_para_display)
    _draw_totals_footer(pdf, width, y_position, total_horas, total_minutos)

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f"relatorio_pontos_{servidor.matricula}.pdf",
    )


gerar_relatorio_pontos_pdf.short_description = "Gerar Relatório de Pontos (PDF)"


# ------------------------------------------------------------------
# CLASSE ADMIN PERSONALIZADA PARA O SERVIDOR
# ------------------------------------------------------------------
class ServidorAdmin(admin.ModelAdmin):
    list_display = (
        "matricula",
        "get_user_email",
        "get_user_first_name",
        "get_user_last_name",
    )
    search_fields = ("matricula", "user__email", "user__first_name", "user__last_name")
    actions = [gerar_relatorio_pontos_pdf]

    @admin.display(description="Email", ordering="user__email")
    def get_user_email(self, obj):
        return obj.user.email

    @admin.display(description="Nome", ordering="user__first_name")
    def get_user_first_name(self, obj):
        return obj.user.first_name

    @admin.display(description="Sobrenome", ordering="user__last_name")
    def get_user_last_name(self, obj):
        return obj.user.last_name


# ------------------------------------------------------------------
# REGISTRO FINAL DOS MODELS
# ------------------------------------------------------------------
admin.site.register(User)
admin.site.register(Visitante)
admin.site.register(Servidor, ServidorAdmin)
