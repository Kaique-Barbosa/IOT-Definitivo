# ===== CONFIGURAÇÕES Wi-Fi =====
WIFI_SSID = "AMD FAMILY"
WIFI_PASS = "87245730"

# ===== CONFIGURAÇÕES MQTT =====
MQTT_SERVER = "broker.hivemq.com"  # Ex: "192.168.1.100" ou "broker.emqx.io"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "estacao_iot_01"
MQTT_TOPIC = b"estacao/sensores"
MQTT_USER = None       # Preencher se o broker exigir autenticação
MQTT_PASSWORD = None   # Preencher se o broker exigir autenticação

# ===== CONFIGURAÇÕES DA FILA =====
FILA_LIMITE = 300  # Máximo de registros na RAM (cada LED = 12 registros)

# ===== INTERVALOS =====
INTERVALO_LEITURA = 2  # Segundos entre cada ciclo do loop principal

# ===== CONFIGURACOES DA FILA e LOOP =====
FILA_LIMITE = 300
INTERVALO_LEITURA = 2
