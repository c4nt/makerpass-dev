from django.db import models
from django.utils import timezone 
from autenticacao.models import Servidor

class Ponto(models.Model):
    bolsista = models.ForeignKey(Servidor, on_delete=models.CASCADE)
    data_hora_do_ponto = models.DateTimeField(auto_now_add=True) 
    eh_entrada = models.BooleanField(default=True)   

    def __str__(self):
        hora_local = timezone.localtime(self.data_hora_do_ponto)
        return f"Nome:  {self.bolsista.user.username} - Data: {hora_local.date()} - Tipo : {'Entrada' if self.eh_entrada else 'Saída'} Hora: {hora_local.time()}" 

class JornadaDiaria(models.Model):
    bolsista = models.ForeignKey(Servidor, on_delete=models.CASCADE)
    data_hora_do_registro = models.DateTimeField(auto_now_add=True)
    horas_trabalhadas = models.DecimalField(decimal_places=2, max_digits=3,null=True, blank=True)
    
    def __str__(self):
        return f"Nome:  {self.bolsista.matricula} - Data: {self.data_hora_do_registro.date()} - Horas trabalhadas: {self.horas_trabalhadas}" 
