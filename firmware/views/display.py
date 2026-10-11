import machine
import ssd1306

oled = None

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

def mostrar_dados(dados, wifi_ok=False, mqtt_ok=False, fila_tam=0):
    if oled is None:
        return

    oled.fill(0)
    
    wifi_txt = "OK" if wifi_ok else "--"
    mqtt_txt = "OK" if mqtt_ok else "--"
    oled.text(f"W:{wifi_txt} M:{mqtt_txt} F:{fila_tam}", 0, 0)
    
    oled.text("-" * 16, 0, 10)
    
    temp = dados.get('temperatura', '--')
    umid = dados.get('dht_umidade', '--')
    bmp_p = dados.get('bmp_pressao', '--')
    chuva = dados.get('chuva_bruta', '--')
    
    oled.text(f"Temp: {temp} C", 0, 20)
    oled.text(f"Umid: {umid} %", 0, 30)
    
    if bmp_p != '--':
        pressao_hpa = round(bmp_p / 100, 1)
        oled.text(f"Pres: {pressao_hpa} hPa", 0, 40)
    else:
        oled.text("Pres: -- hPa", 0, 40)
    
    oled.text(f"Chuva: {chuva}", 0, 50)
    
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
