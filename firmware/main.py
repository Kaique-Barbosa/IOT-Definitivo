import time
import gc
import json
import machine
from models import sensors
from models import queue_manager
from views import display
from views import led_matrix
from views import buzzer
from controllers import connectivity
import config

print("--- Iniciando a Miniestacao Meteorologica IoT ---")
print("Fase 4+: Sensores + OLED + Matriz + Buzzer + NTP + Captive Portal")

def inicializar_hardware():
    """Inicializa todos os periféricos físicos."""
    sensors.init()
    display.init()
    led_matrix.init()
    buzzer.init()

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

            novas_creds = portal.aguardar_configuracao()
            portal.desativar_ap()

            ssid_digitado = novas_creds.get("ssid", "").strip()
            senha_digitada = novas_creds.get("senha", "").strip()

            print(f"[Portal] Validando conexão com '{ssid_digitado}'...")
            display.mostrar_aviso("Testando...", ssid_digitado)

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

# ===== BOTÕES FÍSICOS (BITDOGLAB v6.3) =====
# Botão A no GPIO 5: Simulação de queda/restabelecimento de rede
botao_a = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
ultimo_clique_a = 0

# Botão B no GPIO 6: Alternância das 3 telas do display OLED
botao_b = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_UP)
ultimo_clique_b = 0

def verificar_botoes():
    """Verifica cliques nos botões A e B com debounce independente."""
    global ultimo_clique_a, ultimo_clique_b
    agora = time.ticks_ms()

    # Verificação do Botão A (GPIO 5)
    if botao_a.value() == 0:
        if time.ticks_diff(agora, ultimo_clique_a) > 300:
            ultimo_clique_a = agora
            em_queda = connectivity.alternar_simulacao()
            if em_queda:
                print("\n" + "="*45)
                print(">>> [BOTÃO A] SIMULAÇÃO DE QUEDA ATIVADA! <<<")
                print(">>> Wi-Fi 'desconectado' -> Fila de RAM em ação <<<")
                print("="*45)
                buzzer.iniciar_alerta_queda()
            else:
                print("\n" + "="*45)
                print(">>> [BOTÃO A] SIMULAÇÃO DESATIVADA! <<<")
                print(">>> Conexão restaurada -> Descarregando fila... <<<")
                print("="*45)
                buzzer.parar_alerta()
                buzzer.bipe_sucesso()

    # Verificação do Botão B (GPIO 6)
    if botao_b.value() == 0:
        if time.ticks_diff(agora, ultimo_clique_b) > 250:
            ultimo_clique_b = agora
            nova_tela = display.alternar_tela()
            print(f"[OLED] Botão B pressionado -> Mudando para Tela {nova_tela}")

def aguardar_com_verificacao(segundos):
    """
    Substitui o time.sleep tradicional fatiando em voltas de 50ms,
    permitindo resposta tátil imediata aos botões e controle preciso do Buzzer.
    """
    fatias = int(segundos / 0.05)
    for _ in range(fatias):
        verificar_botoes()
        buzzer.atualizar()
        time.sleep(0.05)

def loop():
    """Loop principal da miniestação meteorológica."""
    inicializar_hardware()

    wifi_ok = inicializar_rede()
    mqtt_ok = False

    if wifi_ok:
        buzzer.bipe_sucesso()
        connectivity.sincronizar_ntp()
        mqtt_ok = connectivity.conectar_mqtt()
        if mqtt_ok:
            buzzer.bipe_sucesso()

    # Rastreia o estado anterior da conexão para acionar alertas sonoros em mudanças reais
    conexao_anterior_ok = (wifi_ok and mqtt_ok)

    while True:
        try:
            verificar_botoes()
            buzzer.atualizar()

            dados = sensors.ler_todos()
            wifi_ok = connectivity.wifi_conectado()

            # Se o Wi-Fi estiver ok mas o MQTT caiu ou ainda não subiu, tenta reconectar
            if wifi_ok and not mqtt_ok:
                mqtt_ok = connectivity.conectar_mqtt()
                if mqtt_ok:
                    buzzer.bipe_sucesso()

            conexao_atual_ok = (wifi_ok and mqtt_ok)

            # Transição: a rede acabou de cair (queda real ou simulação)
            if conexao_anterior_ok and not conexao_atual_ok:
                print("[ALERTA] Conexão caiu! Acionando alarme no Buzzer...")
                buzzer.iniciar_alerta_queda()

            # Transição: a rede acabou de voltar
            elif not conexao_anterior_ok and conexao_atual_ok:
                print("[INFO] Conexão restabelecida! Silenciando alarme...")
                buzzer.parar_alerta()
                buzzer.bipe_sucesso()

            conexao_anterior_ok = conexao_atual_ok

            # Adiciona carimbo de data/hora oficial no payload dos dados
            dados["horario"] = connectivity.obter_data_hora_iso()

            # Envio MQTT ou enfileiramento na RAM
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
            ram_livre = gc.mem_free()
            ram_usada = gc.mem_alloc()

            # Atualização visual das saídas físicas
            display.mostrar_dados(
                dados=dados,
                wifi_ok=wifi_ok,
                mqtt_ok=mqtt_ok,
                fila_tam=fila_tam,
                ip_local=connectivity.obter_ip(),
                ssid_atual=connectivity.obter_ssid_ativo(),
                ram_livre=ram_livre,
                hora_str=connectivity.obter_hora_curta()
            )

            led_matrix.atualizar_barra(queue_manager.percentual())

            status_wifi = "SIM_OFF" if connectivity.esta_em_simulacao() else ("OK" if wifi_ok else "OFF")
            hora_completa = connectivity.obter_hora_formatada()
            print(f"\n[{hora_completa}] Registro: {dados}")
            print(f"Fila: {fila_tam}/{config.FILA_LIMITE} | WiFi: {status_wifi} | MQTT: {'OK' if mqtt_ok else 'OFF'}")

            gc.collect()
            print(f"RAM Livre: {ram_livre} bytes | RAM Usada: {ram_usada} bytes")

        except Exception as e:
            print("Erro no loop:", e)

        aguardar_com_verificacao(config.INTERVALO_LEITURA)

if __name__ == "__main__":
    loop()
