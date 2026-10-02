import time
import gc
import json
from models import sensors
from models import queue_manager
from views import display
from views import led_matrix
from controllers import connectivity
import config

print("--- Iniciando a Miniestacao Meteorologica IoT ---")
print("Fase 4: Sensores + OLED + Matriz LEDs + MQTT + Fila RAM")

def loop():
    sensors.init()
    display.init()
    led_matrix.init()
    
    wifi_ok = connectivity.conectar_wifi()
    mqtt_ok = False
    if wifi_ok:
        mqtt_ok = connectivity.conectar_mqtt()
    
    while True:
        try:
            dados = sensors.ler_todos()
            wifi_ok = connectivity.wifi_conectado()
            
            if wifi_ok and not mqtt_ok:
                mqtt_ok = connectivity.conectar_mqtt()
            
            if wifi_ok and mqtt_ok:
                sucesso = connectivity.publicar(dados)
                if sucesso:
                    enviados = 0
                    while queue_manager.tamanho() > 0 and enviados < 5:
                        registro_antigo = queue_manager.fila[0]
                        if connectivity.publicar(registro_antigo):
                            queue_manager.fila.pop(0)
                            enviados += 1
                        else:
                            mqtt_ok = False
                            break
                    if enviados > 0:
                        print(f">>> Enviados {enviados} registros pendentes da fila!")
                else:
                    mqtt_ok = False
                    queue_manager.adicionar(dados)
            else:
                queue_manager.adicionar(dados)
                if not wifi_ok:
                    wifi_ok = connectivity.conectar_wifi(tentativas_max=3)
            
            fila_tam = queue_manager.tamanho()
            display.mostrar_dados(dados, wifi_ok, mqtt_ok, fila_tam)
            led_matrix.atualizar_barra(queue_manager.percentual())
            
            print(f"\nRegistro: {dados}")
            print(f"Fila: {fila_tam}/{config.FILA_LIMITE} | WiFi: {'OK' if wifi_ok else 'OFF'} | MQTT: {'OK' if mqtt_ok else 'OFF'}")
            
            gc.collect()
            ram_livre = gc.mem_free()
            ram_usada = gc.mem_alloc()
            print(f"RAM Livre: {ram_livre} bytes | RAM Usada: {ram_usada} bytes")
            
        except Exception as e:
            print("Erro no loop:", e)
            
        time.sleep(config.INTERVALO_LEITURA)

if __name__ == "__main__":
    loop()

