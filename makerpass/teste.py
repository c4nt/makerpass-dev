# test_cooldown.py

import requests
import time
import json

API_URL = "http://127.0.0.1:8000/makerpass/api/registrar/"
MATRICULAS = ["20211014040051", "20211014040013"]

def registrar_ponto(matricula):
    """
    Função auxiliar que envia uma requisição de ponto para a API
    e imprime o resultado de forma clara.
    """
    print(f"▶️  Tentando registrar ponto para a matrícula: {matricula}")
    payload = {"matricula": matricula}
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        status_code = response.status_code
        response_json = response.json()

        if status_code == 200:
            print(f"✅ SUCESSO (Status {status_code}): {response_json.get('message')}")
        else:
            # Para erros como 429 (Too Many Requests) ou 404 (Not Found)
            print(f"❌ FALHA (Status {status_code}): {response_json.get('message')}")

    except requests.exceptions.RequestException as e:
        print(f"🚨 ERRO DE CONEXÃO: Não foi possível conectar à API. Erro: {e}")
    
    print("-" * 60)


if __name__ == "__main__":
    print("🚀 INICIANDO SCRIPT DE TESTE DA LÓGICA DE COOLDOWN 🚀")
    
    # --- TESTE 1: TENTATIVA DE REGISTRO DUPLO ---
    print("\n--- [TESTE 1] Registro duplo para o mesmo usuário em menos de 1 min ---")
    # Primeira tentativa, deve funcionar
    registrar_ponto(MATRICULAS[0])
    
    print("...aguardando 5 segundos...")
    time.sleep(5)
    
    # Segunda tentativa, deve ser bloqueada pela lógica de cooldown
    registrar_ponto(MATRICULAS[0])
    
    # --- TESTE 2: REGISTRO PARA USUÁRIOS DIFERENTES ---
    print("\n--- [TESTE 2] Registros para usuários diferentes em curto intervalo ---")
    # Tentativa para o primeiro usuário, deve funcionar
    registrar_ponto(MATRICULAS[0])
    
    print("...aguardando 5 segundos...")
    time.sleep(5)
    
    # Tentativa para o segundo usuário, deve funcionar pois o cooldown é por pessoa
    registrar_ponto(MATRICULAS[1])
    
    # --- TESTE 3: REGISTRO APÓS O FIM DO COOLDOWN ---
    print("\n--- [TESTE 3] Novo registro para o mesmo usuário após 1 min ---")
    # Primeira tentativa, deve funcionar
    registrar_ponto(MATRICULAS[0])
    
    print("...aguardando 65 segundos (para garantir o fim do cooldown)...")
    time.sleep(65)
    
    # Segunda tentativa, deve funcionar pois o tempo de espera já passou
    registrar_ponto(MATRICULAS[0])
    
    print("\n✅ Testes finalizados.")