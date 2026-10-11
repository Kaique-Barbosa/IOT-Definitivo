import network
import time
import json
from umqtt.simple import MQTTClient
import config

try:
    import ntptime
except ImportError:
    ntptime = None

wlan = None
cliente_mqtt = None

CREDENCIAIS_FILE = "credenciais.json"

# Flag que indica se o relógio já foi sincronizado via NTP
ntp_sincronizado = False

# ===== SINCRONIZAÇÃO DE TEMPO REAL (NTP) =====

def sincronizar_ntp():
    """
    Tenta sincronizar o relógio interno do Pico W com servidores NTP.
    Não trava caso o roteador bloqueie a porta UDP 123 ou o servidor demore.
    """
    global ntp_sincronizado
    if ntptime is None:
        print("[NTP] Modulo ntptime nao disponivel.")
        return False
    try:
        ntptime.settime()
        ntp_sincronizado = True
        print(f"[NTP] Relógio sincronizado com sucesso! Hora UTC-3: {obter_hora_formatada()}")
        return True
    except Exception as e:
        print("[NTP] Aviso: Falha ao sincronizar via NTP:", e)
        return False

def obter_timestamp_epoch():
    """Retorna epoch ajustado para o fuso horário de Brasília (UTC-3)."""
    return time.time() - (3 * 3600)

def obter_hora_formatada():
    """Retorna string no formato 'HH:MM:SS' em horário de Brasília."""
    if not ntp_sincronizado:
        return "--:--:--"
    t = time.localtime(obter_timestamp_epoch())
    return f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}"

def obter_hora_curta():
    """Retorna string no formato 'HH:MM' para cabeçalhos compactos do OLED."""
    if not ntp_sincronizado:
        return "--:--"
    t = time.localtime(obter_timestamp_epoch())
    return f"{t[3]:02d}:{t[4]:02d}"

def obter_data_hora_iso():
    """Retorna data e hora completa formatada 'YYYY-MM-DD HH:MM:SS'."""
    if not ntp_sincronizado:
        return None
    t = time.localtime(obter_timestamp_epoch())
    return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d} {t[3]:02d}:{t[4]:02d}:{t[5]:02d}"

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

def apagar_credenciais():
    """Remove o arquivo credenciais.json do flash caso esteja corrompido ou invalido."""
    try:
        import os
        os.remove(CREDENCIAIS_FILE)
        print("Arquivo de credenciais removido do flash.")
    except:
        pass

# ===== CONTROLE DE SIMULAÇÃO (BOTÃO A) =====
simulacao_offline = False

def alternar_simulacao():
    """Alterna o estado de simulação de queda de conexão (True/False)."""
    global simulacao_offline
    simulacao_offline = not simulacao_offline
    return simulacao_offline

def esta_em_simulacao():
    """Retorna True se estiver simulando queda de rede."""
    return simulacao_offline

# ===== WI-FI =====

def obter_ip():
    """Retorna o IP local atribuído à placa ou vazio se desconectado."""
    if wlan is not None and wlan.isconnected():
        return wlan.ifconfig()[0]
    return "0.0.0.0"

def obter_ssid_ativo():
    """Retorna o nome do SSID atualmente configurado."""
    ssid, _ = ler_credenciais()
    return ssid

def conectar_wifi(tentativas_max=10, ssid_custom=None, senha_custom=None):
    """
    Tenta conectar ao Wi-Fi.
    Se estiver em simulação forçada pelo Botão A, não tenta conectar.
    Se ssid_custom for fornecido, usa essas credenciais (validação temporária).
    Caso contrário, busca no flash (credenciais.json) ou em config.py.
    Retorna True se conectou, False se falhou.
    """
    global wlan
    if simulacao_offline:
        return False

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        return True

    if ssid_custom is not None:
        ssid, senha = ssid_custom, senha_custom
    else:
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
    """
    Verifica se o Wi-Fi ainda está ativo.
    Retorna False imediatamente se estiver sob simulação forçada de queda.
    """
    if simulacao_offline:
        return False
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
