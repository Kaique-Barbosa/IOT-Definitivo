import network
import time
import json
from umqtt.simple import MQTTClient
import config

wlan = None
cliente_mqtt = None

def conectar_wifi(tentativas_max=10):
    """
    Tenta conectar ao Wi-Fi.
    tentativas_max controla quanto tempo esperar (em segundos).
    Retorna True se conectou, False se falhou.
    """
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        return True
    
    # Verifica se o SSID é placeholder (evita travar 10s à toa)
    if config.WIFI_SSID == "SEU_SSID_AQUI":
        print("Wi-Fi: SSID não configurado em config.py")
        return False
    
    print(f"Conectando ao Wi-Fi: {config.WIFI_SSID}...")
    wlan.connect(config.WIFI_SSID, config.WIFI_PASS)
    
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
        cliente_mqtt = None  # Marca como desconectado para tentar reconectar
        return False
