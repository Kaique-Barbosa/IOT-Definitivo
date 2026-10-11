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
    sensors.init()
    display.init()
    led_matrix.init()

def inicializar_rede():
    """
    Tenta conectar ao Wi-Fi salvo.
    Se falhar, ativa o Captive Portal em loop contínuo até que uma credencial
    válida seja inserida pelo usuário, sem reiniciar a placa por hardware.
    """
    wifi_ok = connectivity.conectar_wifi()

    if not wifi_ok:
        from controllers import portal

        while not wifi_ok:
            print("\n[Portal] Ativando Captive Portal...")
            ip = portal.ativar_ap()
            display.mostrar_modo_portal(ip)

            # Bloqueia aqui até o usuário enviar as credenciais pelo celular
            novas_creds = portal.aguardar_configuracao()
            portal.desativar_ap()

            ssid_digitado = novas_creds.get("ssid", "").strip()
            senha_digitada = novas_creds.get("senha", "").strip()

            print(f"[Portal] Validando conexão com '{ssid_digitado}'...")
            display.mostrar_aviso("Testando...", ssid_digitado)

            # Testa a conexão em RAM (sem salvar no flash antes de saber se funciona)
            wifi_ok = connectivity.conectar_wifi(
                tentativas_max=10,
                ssid_custom=ssid_digitado,
                senha_custom=senha_digitada
            )

            if wifi_ok:
                print(f"[Portal] Sucesso! Conectado a '{ssid_digitado}'. Salvando no flash...")
                display.mostrar_aviso("Wi-Fi Conectado!", "Salvando...")
                connectivity.salvar_credenciais(ssid_digitado, senha_digitada)
                time.sleep(1)
            else:
                print(f"[Portal] Falha ao conectar em '{ssid_digitado}'. Reabrindo portal...")
                display.mostrar_aviso("Falha na senha!", "Reabrindo Portal")
                time.sleep(2)

    return wifi_ok

# ===== BOTÃO A (SIMULAÇÃO DE QUEDA DE REDE - GPIO 5) =====
botao_a = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
ultimo_clique_botao = 0

def verificar_botao_a():
    """Verifica se o Botão A foi pressionado (LOW) com debounce de 300ms."""
    global ultimo_clique_botao
    if botao_a.value() == 0:
        agora = time.ticks_ms()
        if time.ticks_diff(agora, ultimo_clique_botao) > 300:
            ultimo_clique_botao = agora
            em_queda = connectivity.alternar_simulacao()
            if em_queda:
                print("\n" + "="*45)
                print(">>> [BOTÃO A] SIMULAÇÃO DE QUEDA ATIVADA! <<<")
                print(">>> Wi-Fi 'desconectado' -> Fila de RAM em ação <<<")
                print("="*45)
            else:
                print("\n" + "="*45)
                print(">>> [BOTÃO A] SIMULAÇÃO DESATIVADA! <<<")
                print(">>> Conexão restaurada -> Descarregando fila... <<<")
                print("="*45)

def aguardar_com_verificacao(segundos):
    """
    Substitui o time.sleep tradicional particionando o intervalo em fatias de 50ms,
    permitindo resposta imediata ao clique do Botão A sem atrasos perceptíveis.
    """
    fatias = int(segundos / 0.05)
    for _ in range(fatias):
        verificar_botao_a()
        time.sleep(0.05)

def loop():
    """Loop principal da estação — roda após conexão bem-sucedida."""
    inicializar_hardware()

    wifi_ok = inicializar_rede()
    mqtt_ok = False
    if wifi_ok:
        mqtt_ok = connectivity.conectar_mqtt()

    while True:
        try:
            verificar_botao_a()
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
                if not wifi_ok and not connectivity.esta_em_simulacao():
                    wifi_ok = connectivity.conectar_wifi(tentativas_max=3)

            fila_tam = queue_manager.tamanho()
            display.mostrar_dados(dados, wifi_ok, mqtt_ok, fila_tam)
            led_matrix.atualizar_barra(queue_manager.percentual())

            status_wifi = "SIM_OFF" if connectivity.esta_em_simulacao() else ("OK" if wifi_ok else "OFF")
            print(f"\nRegistro: {dados}")
            print(f"Fila: {fila_tam}/{config.FILA_LIMITE} | WiFi: {status_wifi} | MQTT: {'OK' if mqtt_ok else 'OFF'}")

            gc.collect()
            ram_livre = gc.mem_free()
            ram_usada = gc.mem_alloc()
            print(f"RAM Livre: {ram_livre} bytes | RAM Usada: {ram_usada} bytes")

        except Exception as e:
            print("Erro no loop:", e)

        aguardar_com_verificacao(config.INTERVALO_LEITURA)

if __name__ == "__main__":
    loop()
