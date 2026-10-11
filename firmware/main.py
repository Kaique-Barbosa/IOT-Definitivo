import time
import gc
import json
import machine
from models import sensors
from models import queue_manager
from views import display
from views import led_matrix
from controllers import connectivity
import config

print("--- Iniciando a Miniestacao Meteorologica IoT ---")
print("Fase 4+: Sensores + OLED + Matriz LEDs + MQTT + Fila RAM + Captive Portal")

def inicializar_hardware():
    """Inicializa todos os periféricos físicos."""
    print("Configurando hardwares de sensoriamento...")
    sensors.init()
    print("Configurando Display OLED...")
    display.init()
    print("Configurando Matriz de LEDs (NeoPixel 5x5)...")
    led_matrix.init()

def inicializar_rede():
    """
    Tenta conectar ao Wi-Fi salvo.
    Se falhar, ativa o Captive Portal para o usuário configurar uma nova rede.
    Retorna True se Wi-Fi conectado ao final, False se algo crítico falhou.
    """
    wifi_ok = connectivity.conectar_wifi()

    if not wifi_ok:
        print("Wi-Fi falhou. Ativando Captive Portal...")
        from controllers import portal

        ip = portal.ativar_ap()
        display.mostrar_modo_portal(ip)

        # Bloqueia aqui até o usuário enviar as credenciais pelo celular
        novas_creds = portal.aguardar_configuracao()
        portal.desativar_ap()

        connectivity.salvar_credenciais(novas_creds["ssid"], novas_creds["senha"])

        # Tenta conectar com as novas credenciais
        wifi_ok = connectivity.conectar_wifi()

        if not wifi_ok:
            # Senha ou rede inválida: reinicia a placa para voltar ao portal
            print("Credenciais inválidas. Reiniciando para voltar ao portal...")
            time.sleep(2)
            machine.reset()

    return wifi_ok

def loop():
    """Loop principal da estação — roda após conexão bem-sucedida."""
    inicializar_hardware()

    wifi_ok = inicializar_rede()
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
                    # Descarrega fila pendente em rajadas de até 5 registros por ciclo
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
