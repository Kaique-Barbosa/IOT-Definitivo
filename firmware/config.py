# ===== CONFIGURAÇÕES Wi-Fi =====
# Usadas como fallback se nenhum credenciais.json for encontrado no flash
WIFI_SSID = "AMD FAMILY"
WIFI_PASS = "87245730"

# ===== CONFIGURAÇÕES MQTT =====
MQTT_SERVER = "147.15.56.168"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "93ea8d12-790c-4766-b440-737e363d98b1"
MQTT_TOPIC = b"estacao/sensores"
MQTT_USER = None
MQTT_PASSWORD = None

# ===== CONFIGURAÇÕES DA FILA =====
# 30 registros para teste visual rápido (1 LED da Matriz = ~1 registro acumulado)
# Após validação do teste, retornar para 300
FILA_LIMITE = 30

# ===== INTERVALOS =====
INTERVALO_LEITURA = 1  # Segundos entre cada ciclo do loop principal
