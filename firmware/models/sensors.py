import machine
import dht
import time

try:
    import bmp280
except ImportError:
    print("Aviso: Módulo bmp280 não encontrado. O BMP não funcionará se a lib não estiver no Pico.")

sensor_dht = None
sensor_chuva = None
sensor_bmp = None

# Cache para armazenar a última leitura com sucesso (Inicia com "--" para a tela não ficar vazia)
ultimo_registro = {
    "temperatura": "--",
    "dht_temp": "--",
    "dht_umidade": "--",
    "bmp_temp": "--",
    "bmp_pressao": "--",
    "chuva_bruta": "--"
}

def init():
    global sensor_dht, sensor_chuva, sensor_bmp
    print("Configurando hardwares de sensoriamento...")
    
    try:
        pino_dht = machine.Pin(18)
        sensor_dht = dht.DHT11(pino_dht)
    except Exception as e:
        print("Falha ao configurar DHT11:", e)
        
    try:
        sensor_chuva = machine.ADC(28)
    except Exception as e:
        print("Falha ao configurar ADC de Chuva:", e)
        
    try:
        i2c = machine.I2C(0, sda=machine.Pin(16), scl=machine.Pin(17), freq=400000)
        sensor_bmp = bmp280.BMP280(i2c)
    except Exception as e:
        print("Falha ao configurar BMP280 (I2C):", e)

def ler_todos():
    global ultimo_registro
    
    # Tentativa de leitura do DHT11
    if sensor_dht is not None:
        try:
            sensor_dht.measure()
            ultimo_registro["dht_temp"] = sensor_dht.temperature()
            ultimo_registro["dht_umidade"] = sensor_dht.humidity()
        except OSError as e:
            # Se o sensor engasgar, imprimimos no terminal para investigar se é esse o motivo da tela estática
            print("Aviso: Falha ao ler DHT11, usando cache. Erro:", e) 
            
    # Tentativa de leitura do BMP280
    if sensor_bmp is not None:
        try:
            ultimo_registro["bmp_temp"] = round(sensor_bmp.temperature, 2)
            ultimo_registro["bmp_pressao"] = round(sensor_bmp.pressure, 2)
        except Exception as e:
            print("Aviso: Falha ao ler BMP280, usando cache. Erro:", e)
            
    # Tentativa de leitura da Chuva
    if sensor_chuva is not None:
        try:
            ultimo_registro["chuva_bruta"] = sensor_chuva.read_u16()
        except Exception as e:
            print("Aviso: Falha ao ler Chuva, usando cache. Erro:", e)
            
    # --- FUSÃO DOS SENSORES DE TEMPERATURA ---
    try:
        t_dht = ultimo_registro.get("dht_temp", "--")
        t_bmp = ultimo_registro.get("bmp_temp", "--")
        if t_dht != "--" and t_bmp != "--":
            # Calcula a média
            media = (float(t_dht) + float(t_bmp)) / 2
            ultimo_registro["temperatura"] = round(media, 2)
        else:
            ultimo_registro["temperatura"] = "--"
    except Exception as e:
        print("Erro ao calcular média de temperatura:", e)
        ultimo_registro["temperatura"] = "--"

    # Retornamos uma CÓPIA do dicionário. Assim, se outro arquivo tentar modificar os dados, não estraga o nosso cache interno.
    return ultimo_registro.copy()

