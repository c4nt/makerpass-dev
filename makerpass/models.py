from django.db import models
from django.utils import timezone
from autenticacao.models import Servidor


class Ponto(models.Model):
    bolsista = models.ForeignKey(Servidor, on_delete=models.CASCADE)
    data_hora_do_ponto = models.DateTimeField(auto_now_add=True)
    eh_entrada = models.BooleanField(default=True)

    def __str__(self):
        hora_local = timezone.localtime(self.data_hora_do_ponto)
        tipo = 'Entrada' if self.eh_entrada else 'Saída'
        return (
            f"Nome: {self.bolsista.user.username} - "
            f"Data: {hora_local.date()} - "
            f"Tipo: {tipo} - "
            f"Hora: {hora_local.time()}"
        )
