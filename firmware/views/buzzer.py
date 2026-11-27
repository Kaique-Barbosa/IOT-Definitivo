import machine
import time

# Buzzer A na BitDogLab v6.3 está no GPIO 21
PINO_BUZZER = 21
buzzer_pwm = None

# Variáveis de controle de alarme de queda (não-bloqueante)
alerta_ativo = False
inicio_alerta = 0
DURACAO_MAX_ALERTA = 10000  # 10 segundos em milissegundos
ultimo_pulso = 0
estado_pulso = False

def init():
    """Inicializa o pino do Buzzer com PWM a 0% de duty cycle (silencioso)."""
    global buzzer_pwm
    try:
        buzzer_pwm = machine.PWM(machine.Pin(PINO_BUZZER))
        buzzer_pwm.duty_u16(0)
    except Exception as e:
        print("Aviso: Falha ao inicializar Buzzer:", e)
        buzzer_pwm = None

def bipe_sucesso():
    """
    Emite um bipe curto, suave e amigável (80ms a 1200Hz).
    Usado quando conecta com sucesso ao Wi-Fi ou Broker MQTT.
    """
    if buzzer_pwm is None:
        return
    try:
        buzzer_pwm.freq(1200)
        buzzer_pwm.duty_u16(32768)  # 50% de volume
        time.sleep(0.08)
        buzzer_pwm.duty_u16(0)
    except:
        pass

def iniciar_alerta_queda():
    """
    Inicia a sequência de alarme de queda de conexão.
    Roda por até 10 segundos sem travar o processador.
    """
    global alerta_ativo, inicio_alerta, ultimo_pulso, estado_pulso
    if not alerta_ativo:
        alerta_ativo = True
        inicio_alerta = time.ticks_ms()
        ultimo_pulso = inicio_alerta
        estado_pulso = True
        if buzzer_pwm:
            try:
                buzzer_pwm.freq(600)
                buzzer_pwm.duty_u16(32768)
            except:
                pass

def parar_alerta():
    """
    Silencia imediatamente o alarme caso a conexão seja restabelecida
    antes dos 10 segundos expirarem.
    """
    global alerta_ativo, estado_pulso
    alerta_ativo = False
    estado_pulso = False
    if buzzer_pwm:
        try:
            buzzer_pwm.duty_u16(0)
        except:
            pass

def esta_em_alerta():
    """Retorna True se o alerta sonoro estiver ativo."""
    return alerta_ativo

def atualizar():
    """
    Controlador não-bloqueante de pulso.
    Deve ser chamado periodicamente no loop principal (a cada volta de 50ms).
    Alterna o som entre 400ms ligado e 400ms desligado.
    Encerra sozinho após 10 segundos.
    """
    global alerta_ativo, ultimo_pulso, estado_pulso
    if not alerta_ativo or buzzer_pwm is None:
        return

    agora = time.ticks_ms()

    # Verifica se atingiu os 10 segundos máximos de alerta
    if time.ticks_diff(agora, inicio_alerta) >= DURACAO_MAX_ALERTA:
        parar_alerta()
        return

    # Alterna o tom a cada 400ms (bipes longos de alerta)
    if time.ticks_diff(agora, ultimo_pulso) >= 400:
        ultimo_pulso = agora
        estado_pulso = not estado_pulso
        try:
            if estado_pulso:
                buzzer_pwm.freq(600)
                buzzer_pwm.duty_u16(32768)
            else:
                buzzer_pwm.duty_u16(0)
        except:
            pass
