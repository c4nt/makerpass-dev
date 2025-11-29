from datetime import timedelta
from typing import Iterable, Tuple


def calcular_total_horas(pontos: Iterable) -> Tuple[int, int]:
    total_duration = timedelta()
    entrada_time = None

    for ponto in pontos:
        if getattr(ponto, "eh_entrada", False):
            entrada_time = getattr(ponto, "data_hora_do_ponto", None)
        elif entrada_time is not None:
            saida_time = getattr(ponto, "data_hora_do_ponto", None)
            if saida_time is not None and entrada_time is not None:
                duration = saida_time - entrada_time
                total_duration += duration
                entrada_time = None

    total_seconds = int(total_duration.total_seconds())
    horas = total_seconds // 3600
    minutos = (total_seconds % 3600) // 60
    return horas, minutos
