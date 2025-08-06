#DJANGO
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView
#APP
from .models import User, Visitante, Servidor


class LoginView(View):
    def get(self, request):
        return render(request, "autenticacao/login.html")

    def post(self, request):
        email = request.POST["email"]
        senha = request.POST["senha"]
        print(email, senha)
        usuario = authenticate(request, username=email, password=senha)

        if usuario is not None:
            login(request, usuario)
            return HttpResponse("Usuário autenticado")
        else:
            messages.error(request, "E-mail ou senha incorretos. Por favor, tente novamente.")
        
        return render(request, "autenticacao/login.html")
        

class CadastroVisitanteView(View):
    def get(self, request):
        return render(request, "autenticacao/cadastro_visitante.html")
    
    def post(self, request):
        primeiro_nome = request.POST["primeiro_nome"]
        ultimo_nome = request.POST["ultimo_nome"]

        # Username sempre em minuscúlo
        username = request.POST["username"].lower()

        email = request.POST["email"]
        cpf = request.POST["cpf"]
        telefone = request.POST["telefone"]
        senha = request.POST["senha"]

        if self.username_existe(username):
            return HttpResponse("Username já cadastrado")

        if self.email_existe(email):
            return HttpResponse("Email já cadastrado")
        
        if self.cpf_existe(cpf):
            return HttpResponse("CPF já cadastrado")
        
        user = User.objects.create_user(
            first_name=primeiro_nome,
            last_name=ultimo_nome,
            username=username,
            email=email,
            telefone=telefone,
            password=senha,
        )

        visitante = Visitante.objects.create(
            cpf=cpf,
            user=user
        )

        # Verificar se o user e o visitante foram criados
        print(user, visitante)
        return redirect('cadastro_sucesso')
    
    def username_existe(self, username):
        """Verificar se algum usuário já possui o username cadastrado"""
        return User.objects.filter(username=username).exists()
    
    def email_existe(self, email):
        """Verificar se algum usuário já possui o email cadastrado"""
        return User.objects.filter(email=email).exists()
    
    def cpf_existe(self, cpf):
        """Verificar se algum visitante já possui o CPF cadastrado"""
        return Visitante.objects.filter(cpf=cpf).exists()
    
class CadastroServidorView(View):
    def get(self, request):
        return render(request, "autenticacao/cadastro_servidor.html")
    
    def post(self, request):
        primeiro_nome = request.POST["primeiro_nome"]
        ultimo_nome = request.POST["ultimo_nome"]
        imagem = request.FILES.get('imagem')

        # Username sempre em minuscúlo
        username = request.POST["username"].lower()

        matricula = request.POST["matricula"]
        email = request.POST["email"]
        cpf = request.POST["cpf"]
        telefone = request.POST["telefone"]
        senha = request.POST["senha"]

        if self.username_existe(username):
            return HttpResponse("Username já cadastrado")

        if self.email_existe(email):
            return HttpResponse("Email já cadastrado")
        
        if self.cpf_existe(cpf):
            return HttpResponse("CPF já cadastrado")
        
        user = User.objects.create_user(
            first_name=primeiro_nome,
            last_name=ultimo_nome,
            username=username,
            email=email,
            telefone=telefone,
            password=senha,
        )

        servidor = Servidor.objects.create(
            matricula=matricula,
            cpf=cpf,
            user=user,
            imagem=imagem,
        )

        # Verificar se o user e o visitante foram criados
        print(user, servidor)
        return redirect('cadastro_sucesso')
    
    def username_existe(self, username):
        """Verificar se algum usuário já possui o username cadastrado"""
        return User.objects.filter(username=username).exists()
    
    def email_existe(self, email):
        """Verificar se algum usuário já possui o email cadastrado"""
        return User.objects.filter(email=email).exists()
    
    def cpf_existe(self, cpf):
        """Verificar se algum visitante já possui o CPF cadastrado"""
        return Visitante.objects.filter(cpf=cpf).exists()
    

class CadastroSucessoView(TemplateView):
    template_name = 'autenticacao/sucesso_cadastro.html'


class TipoCadastroView(TemplateView):
    template_name = 'autenticacao/escolha_tipo_conta.html'