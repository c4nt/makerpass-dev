from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=11) # 11998765432 (DDD + 9 + número)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

class Visitante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=11, unique=True, null=True, blank=True) # 86245243312 (apenas números)

    def __str__(self):
        return str(self.user) + " - " + self.cpf # joao@gmail.com - 86245243312

class Servidor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=14) # 20231024090007
    cpf = models.CharField(max_length=11, unique=True, null=True, blank=True) # 86245243312 (apenas números)
    id_sensor_biometrico = models.IntegerField(unique=True, null=True, blank=True)
    imagem = models.ImageField(upload_to='servidores/', null=True, blank=True)


    def __str__(self):
        return str(self.user) + " - " + self.matricula # joao@gmail.com - 20231024090007
