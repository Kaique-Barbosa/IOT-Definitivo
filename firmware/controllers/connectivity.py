import network
import time
import json
from umqtt.simple import MQTTClient
import config

wlan = None
cliente_mqtt = None

CREDENCIAIS_FILE = "credenciais.json"

# ===== GERENCIAMENTO DE CREDENCIAIS =====

def ler_credenciais():
    """
    Lê o arquivo credenciais.json do flash da placa.
    Se o arquivo existir, usa os dados salvos pelo portal.
    Se não existir (primeira execução), usa os valores padrão de config.py.
    Retorna uma tupla: (ssid, senha)
    """
    try:
        with open(CREDENCIAIS_FILE, "r") as f:
            dados = json.load(f)
            ssid = dados.get("ssid", config.WIFI_SSID)
            senha = dados.get("senha", config.WIFI_PASS)
            print(f"Credenciais carregadas do flash: SSID='{ssid}'")
            return ssid, senha
    except:
        print("Sem credenciais salvas. Usando padrão de config.py")
        return config.WIFI_SSID, config.WIFI_PASS

def salvar_credenciais(ssid, senha):
    """
    Grava novas credenciais Wi-Fi no flash da placa (credenciais.json).
    Esse arquivo sobrescreve os valores padrão de config.py na próxima inicialização.
    """
    try:
        with open(CREDENCIAIS_FILE, "w") as f:
            json.dump({"ssid": ssid, "senha": senha}, f)
        print(f"Credenciais salvas no flash: SSID='{ssid}'")
        return True
    except Exception as e:
        print("Erro ao salvar credenciais:", e)
        return False

# ===== WI-FI =====

def conectar_wifi(tentativas_max=10):
    """
    Tenta conectar ao Wi-Fi usando as credenciais do flash (ou config.py como fallback).
    Retorna True se conectou, False se falhou.
    """
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        return True

    ssid, senha = ler_credenciais()

    if not ssid or ssid in ("SEU_SSID_AQUI", "NOME_DA_SUA_REDE_AQUI"):
        print("Wi-Fi: SSID não configurado.")
        return False

    print(f"Conectando ao Wi-Fi: {ssid}...")
    wlan.connect(ssid, senha)

    tentativas = 0
    while not wlan.isconnected() and tentativas < tentativas_max:
        time.sleep(1)
        tentativas += 1

    if wlan.isconnected():
        print("Wi-Fi conectado! IP:", wlan.ifconfig()[0])
        return True
    else:
        print("Falha ao conectar no Wi-Fi.")
        return False

def wifi_conectado():
    """Verifica se o Wi-Fi ainda está ativo."""
    return wlan is not None and wlan.isconnected()

# ===== MQTT =====

def conectar_mqtt():
    """
    Cria o cliente MQTT e tenta conectar ao broker.
    Retorna True se conectou, False se falhou.
    """
    global cliente_mqtt

    if config.MQTT_SERVER == "SEU_BROKER_AQUI":
        print("MQTT: Broker não configurado em config.py")
        return False

    try:
        cliente_mqtt = MQTTClient(
            config.MQTT_CLIENT_ID,
            config.MQTT_SERVER,
            port=config.MQTT_PORT,
            user=config.MQTT_USER,
            password=config.MQTT_PASSWORD
        )
        cliente_mqtt.connect()
        print("MQTT conectado ao broker:", config.MQTT_SERVER)
        return True
    except Exception as e:
        print("Falha ao conectar no MQTT:", e)
        cliente_mqtt = None
        return False

def publicar(registro):
    """
    Tenta publicar um registro via MQTT com QoS 0.
    Retorna True se publicou, False se falhou.
    """
    global cliente_mqtt
    if cliente_mqtt is None:
        return False
    try:
        payload = json.dumps(registro)
        cliente_mqtt.publish(config.MQTT_TOPIC, payload, qos=0)
        return True
    except Exception:
        cliente_mqtt = None  # Marca como desconectado para tentar reconectar no próximo ciclo
        return False
