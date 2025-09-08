from django import forms
from django.utils import timezone

class MonthSelectorForm(forms.Form):
    """
    Formulário para selecionar um mês e ano específicos para o relatório.
    """
    # Cria uma lista de tuplas para os meses (valor, nome_exibido)
    MESES_CHOICES = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    
    # Gera uma lista de anos, por exemplo, dos últimos 5 anos até o ano atual.
    ANO_ATUAL = timezone.now().year
    ANOS_CHOICES = [(i, str(i)) for i in range(ANO_ATUAL - 5, ANO_ATUAL + 1)]

    # Campo para selecionar o mês, com o mês atual como padrão.
    mes = forms.ChoiceField(
        choices=MESES_CHOICES, 
        initial=timezone.now().month,
        label="Mês do Relatório"
    )
    
    # Campo para selecionar o ano, com o ano atual como padrão.
    ano = forms.ChoiceField(
        choices=ANOS_CHOICES, 
        initial=ANO_ATUAL,
        label="Ano do Relatório"
    )