import machine
import ssd1306

oled = None

# Modos de tela: 0 = Clima / Resumo, 1 = Métricas Técnicas, 2 = Diagnóstico de Rede & Sistema
modo_tela = 0
TOTAL_TELAS = 3

def init():
    global oled
    print("Configurando Display OLED...")
    try:
        i2c = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15), freq=400000)
        oled = ssd1306.SSD1306_I2C(128, 64, i2c)
        
        oled.fill(0)
        oled.text("Iniciando...", 0, 0)
        oled.text("Estacao IoT", 0, 15)
        oled.show()
    except Exception as e:
        print("Falha ao inicializar o Display OLED:", e)

def alternar_tela():
    """Alterna ciclicamente entre as 3 telas do OLED (0 -> 1 -> 2 -> 0)."""
    global modo_tela
    modo_tela = (modo_tela + 1) % TOTAL_TELAS
    return modo_tela

def obter_modo_tela():
    """Retorna o índice da tela atualmente selecionada."""
    return modo_tela

def mostrar_dados(dados, wifi_ok=False, mqtt_ok=False, fila_tam=0, ip_local="", ssid_atual="", ram_livre=0, hora_str="--:--"):
    """
    Renderiza uma das 3 telas no display OLED de 128x64 pixels com base no valor de modo_tela.
    """
    if oled is None:
        return

    oled.fill(0)

    # Status compactos para cabeçalhos
    wifi_txt = "OK" if wifi_ok else "--"
    mqtt_txt = "OK" if mqtt_ok else "--"

    # ==========================================
    # TELA 0: VISÃO GERAL DO CLIMA
    # ==========================================
    if modo_tela == 0:
        # Cabeçalho: W:OK M:OK F:0  14:35
        oled.text(f"W:{wifi_txt} M:{mqtt_txt} F:{fila_tam}", 0, 0)
        oled.text(hora_str, 88, 0)
        oled.text("-" * 16, 0, 10)

        temp = dados.get('temperatura', '--')
        umid = dados.get('dht_umidade', '--')
        chuva = dados.get('chuva_bruta', '--')

        oled.text(f"Temp: {temp} C", 0, 22)
        oled.text(f"Umid: {umid} %", 0, 36)
        oled.text(f"Chuva ADC: {chuva}", 0, 50)

    # ==========================================
    # TELA 1: MÉTRICAS TÉCNICAS E PRESSÃO
    # ==========================================
    elif modo_tela == 1:
        oled.text("[DADOS TECNICOS]", 0, 0)
        oled.text("-" * 16, 0, 10)

        bmp_p = dados.get('bmp_pressao', '--')
        bmp_t = dados.get('bmp_temp', '--')
        dht_t = dados.get('dht_temp', '--')

        if bmp_p != '--':
            pressao_hpa = round(bmp_p / 100, 1)
            oled.text(f"Pres: {pressao_hpa}hPa", 0, 20)
            # Estimativa de altitude barométrica hipsométrica aproximada: h = 44330 * (1 - (p/1013.25)^(1/5.255))
            try:
                altitude = round(44330 * (1.0 - (pressao_hpa / 1013.25) ** 0.1903), 0)
                oled.text(f"Alt: ~{int(altitude)} m", 0, 32)
            except:
                oled.text("Alt: -- m", 0, 32)
        else:
            oled.text("Pres: -- hPa", 0, 20)
            oled.text("Alt: -- m", 0, 32)

        oled.text(f"BMP:{bmp_t}C DHT:{dht_t}C", 0, 48)

    # ==========================================
    # TELA 2: DIAGNÓSTICO DE REDE E SISTEMA
    # ==========================================
    elif modo_tela == 2:
        oled.text("[DIAGNOSTICO SIST]", 0, 0)
        oled.text("-" * 16, 0, 10)

        ssid_curto = ssid_atual[:11] if ssid_atual else "--"
        oled.text(f"SSID: {ssid_curto}", 0, 20)
        oled.text(f"IP:{ip_local}", 0, 32)

        ram_kb = round(ram_livre / 1024, 1) if ram_livre else 0
        oled.text(f"Fila:{fila_tam} RAM:{ram_kb}k", 0, 48)

    oled.show()

def mostrar_modo_portal(ip="192.168.4.1"):
    """
    Exibe a tela do Captive Portal no OLED.
    Mostra o nome da rede criada pelo Pico W e o IP de acesso para configuração.
    """
    if oled is None:
        return
    oled.fill(0)
    oled.text("Modo Portal WiFi", 0, 0)
    oled.text("================", 0, 10)
    oled.text("Rede:", 0, 22)
    oled.text("EstacaoIoT-Cfg", 0, 32)
    oled.text("Acesse:", 0, 44)
    oled.text(ip, 0, 54)
    oled.show()

def mostrar_aviso(titulo, subtitulo=""):
    """Exibe uma mensagem rápida centralizada de aviso/status no OLED."""
    if oled is None:
        return
    oled.fill(0)
    oled.text("=== AVISO ===", 10, 5)
    oled.text(titulo[:16], 0, 25)
    if subtitulo:
        oled.text(subtitulo[:16], 0, 42)
    oled.show()
