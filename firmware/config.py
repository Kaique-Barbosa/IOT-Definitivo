# ===== CONFIGURAÇÕES Wi-Fi =====
WIFI_SSID = "SEU_SSID_AQUI"
WIFI_PASS = "SUA_SENHA_AQUI"

# ===== CONFIGURAÇÕES MQTT =====
MQTT_SERVER = "SEU_BROKER_AQUI"  # Ex: "192.168.1.100" ou "broker.emqx.io"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "estacao_iot_01"
MQTT_TOPIC = b"estacao/sensores"
MQTT_USER = None       # Preencher se o broker exigir autenticação
MQTT_PASSWORD = None   # Preencher se o broker exigir autenticação

# ===== CONFIGURAÇÕES DA FILA =====
FILA_LIMITE = 300  # Máximo de registros na RAM (cada LED = 12 registros)

# ===== INTERVALOS =====
INTERVALO_LEITURA = 2  # Segundos entre cada ciclo do loop principal
