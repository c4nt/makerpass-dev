import serial
import os
import requests
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
            # R1702: Reduzindo aninhamento com 'continue'
            if arduino.in_waiting <= 0:
                time.sleep(0.1)
                continue

            linha_recebida = arduino.readline().decode('utf-8').strip()
            print(f"📩 [Serial] Recebido do Arduino: '{linha_recebida}'")

            if not linha_recebida.startswith("ID:"):
                time.sleep(0.1)
                continue

            # Lógica principal
            sensor_id = linha_recebida.replace("ID:", "").strip()
            print(f"📩 [Serial] Recebido do Arduino: '{linha_recebida}'")
            payload = {"id_sensor": sensor_id}
            
            try:
                response = requests.post(API_URL, json=payload, timeout=10)
                # C0301: Quebrando linha longa
                if response.status_code == 200:
                    print("🚀 [API] Sucesso! Resposta:", response.json())
                    ordem_recebida = response.json().get("ordem")
                    if ordem_recebida:
                        msg = f"✨ [Sistema -> Arduino] Ordem: '{ordem_recebida}'"
                        print(msg)
                        arduino.write(f"{ordem_recebida}\n".encode('utf-8'))
                else:
                    # C0301: Quebrando linha longa
                    print(
                        f"⚠️  [API] Erro! Status: {response.status_code}, "
                        f"Resposta: {response.text}"
                    )
            except requests.exceptions.RequestException as e:
                print(f"🚨 [API] Falha de conexão: {e}")
            print("-" * 20)

        except KeyboardInterrupt:
            print("\nEncerrando o programa.")
            break
        # W0718: Ignorando aviso de exceção genérica propositalmente
        except Exception as e: # pylint: disable=broad-exception-caught
            print(f"Ocorreu um erro inesperado: {e}")
            break       
    
    arduino.close()
    print("[Serial] Conexão encerrada.")

if __name__ == "__main__":
    main()