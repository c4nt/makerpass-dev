import serial
import os
import requests
import json
import time
from serial.tools import list_ports

API_URL = "http://127.0.0.1:8000/makerpass/api/registrar/"
BAUD_RATE = 115200


def auto_detect_serial():
    for p in list_ports.comports():
        desc = p.description.lower()

        if "usb" in desc or "cp210" in desc or "ch340" in desc or "ftdi" in desc:
            return p.device
    return None


def conectar_arduino():
    port = auto_detect_serial() or ("COM3" if os.name == "nt" else "/dev/ttyUSB0")
    try:
        arduino = serial.Serial(port, BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"✅ [Serial] Conectado ao Arduino em {port}")
        return arduino
    except serial.SerialException as e:
        print(f"🚨 [Serial] Erro ao conectar: {e}")
        print("🚨 Verifique se o Arduino está conectado e se a porta está correta.")
        return None


def main():
    arduino = conectar_arduino()
    if not arduino:
        print("Saindo do programa: sem conexão com o Arduino.")
        return
    print("\n--- Cliente iniciado. Aguardando dados do sensor... ---")

    while True:
        try:
            if arduino.in_waiting > 0:
                linha_recebida = arduino.readline().decode("utf-8").strip()
                print(f"📩 [Serial] Recebido do Arduino: '{linha_recebida}'")

                if linha_recebida.startswith("ID:"):
                    id = linha_recebida.replace("ID:", "").strip()
                    print(f"📩 [Serial] Recebido do Arduino: '{linha_recebida}'")
                    payload = {"id_sensor": id}
                    try:
                        response = requests.post(API_URL, json=payload, timeout=10)
                        if response.status_code == 200:
                            print("🚀 [API] Sucesso! Resposta:", response.json())

                            ordem_recebida = response.json().get("ordem")
                            if ordem_recebida:
                                print(
                                    f"✨ [Sistema -> Arduino] Ordem recebida da API: '{ordem_recebida}'"
                                )
                                arduino.write(f"{ordem_recebida}\n".encode("utf-8"))
                        else:
                            print(
                                f"⚠️  [API] Erro! Status: {response.status_code}, Resposta: {response.text}"
                            )
                    except requests.exceptions.RequestException as e:
                        print(f"🚨 [API] Falha de conexão: {e}")
                    print("-" * 20)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nEncerrando o programa.")
            break
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            break
    arduino.close()
    print("[Serial] Conexão encerrada.")


if __name__ == "__main__":
    main()


# def obter_matricula_do_sensor():
#     """
#     FUNÇÃO DE EXEMPLO - A LÓGICA REAL DEPENDE DO SEU SENSOR.

#     Esta função representa a interação com o seu hardware.
#     Você deverá substituí-la pela função do SDK/biblioteca do seu sensor
#     que captura a digital e retorna a matrícula associada.

#     Para nosso teste, vamos simular que ele leu uma matrícula.
#     """
#     print("Aguardando digital no sensor...")
#     # Simula uma espera e depois retorna uma matrícula de teste
#     time.sleep(5)
#     matricula_lida = "20211014040051" # Matrícula de exemplo
#     print(f"Digital lida! Matrícula: {matricula_lida}")
#     return matricula_lida


# # --- Loop Principal do Cliente ---
# if __name__ == "__main__":
#     print("Iniciando cliente do sensor biométrico...")
#     while True:
#         # 1. Tenta obter a matrícula a partir do sensor
#         matricula = obter_matricula_do_sensor()

#         if matricula:
#             # 2. Prepara os dados (payload) para enviar no formato JSON
#             payload = {
#                 "matricula": matricula
#             }

#             try:
#                 # 3. Envia a requisição POST para a API Django
#                 print(f"Enviando matricula {matricula} para a API em {API_URL}...")

#                 # O parâmetro 'json=payload' automaticamente:
#                 # - Converte o dicionário Python para uma string JSON.
#                 # - Define o cabeçalho 'Content-Type' para 'application/json'.
#                 response = requests.post(API_URL, json=payload, timeout=10)

#                 # 4. Verifica a resposta da API
#                 if response.status_code == 200:
#                     # Se a resposta for 200 OK, exibe a resposta JSON do servidor
#                     print("✅ Sucesso! Resposta da API:")
#                     print(response.json())
#                 else:
#                     # Se houver um erro (ex: 404 Matrícula não encontrada), exibe o erro
#                     print(f"❌ Erro! A API retornou o status {response.status_code}")
#                     print("Resposta:", response.text)

#             except requests.exceptions.RequestException as e:
#                 # Captura erros de conexão (ex: servidor Django offline, sem rede)
#                 print(f"🚨 FALHA DE CONEXÃO: Não foi possível conectar à API.")
#                 print(f"Erro técnico: {e}")

#         # Uma pequena pausa para não sobrecarregar o sistema.
#         # Na prática, a função do sensor já pode ser bloqueante (esperar pela digital).
#         print("-" * 20)
#         time.sleep(1)
