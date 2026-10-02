import machine
import neopixel
import config

NUM_LEDS = 25
np = None

ORDEM_PREENCHIMENTO = [
    4, 3, 2, 1, 0,       # Linha 0 (base)
    5, 6, 7, 8, 9,       # Linha 1
    14, 13, 12, 11, 10,  # Linha 2
    15, 16, 17, 18, 19,  # Linha 3
    24, 23, 22, 21, 20   # Linha 4 (topo)
]

COR_VERDE = (0, 8, 0)
COR_VERMELHO = (8, 0, 0)

def init():
    global np
    print("Configurando Matriz de LEDs (NeoPixel 5x5)...")
    try:
        np = neopixel.NeoPixel(machine.Pin(7), NUM_LEDS)
        np.fill(COR_VERDE)
        np.write()
    except Exception as e:
        print("Falha ao inicializar Matriz de LEDs:", e)

def atualizar_barra(percentual):
    if np is None:
        return
    
    leds_vermelhos = int(percentual * NUM_LEDS)
    
    if leds_vermelhos > NUM_LEDS:
        leds_vermelhos = NUM_LEDS
    if leds_vermelhos < 0:
        leds_vermelhos = 0
    
    for i in range(NUM_LEDS):
        indice_neopixel = ORDEM_PREENCHIMENTO[i]
        if i < leds_vermelhos:
            np[indice_neopixel] = COR_VERMELHO
        else:
            np[indice_neopixel] = COR_VERDE
    
    np.write()

