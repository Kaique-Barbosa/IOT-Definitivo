import config

# A fila é uma lista simples. O índice 0 é o registro mais antigo.
fila = []

def adicionar(registro):
    """
    Adiciona um registro no final da fila.
    Se a fila atingiu o limite, descarta o mais antigo (FIFO circular).
    """
    global fila
    if len(fila) >= config.FILA_LIMITE:
        fila.pop(0)  # Remove o registro mais antigo
    fila.append(registro)

def tamanho():
    """Retorna quantos registros estão na fila."""
    return len(fila)

def percentual():
    """Retorna o percentual de preenchimento (0.0 a 1.0) para a Matriz de LEDs."""
    return len(fila) / config.FILA_LIMITE

def limpar():
    """Esvazia a fila completamente."""
    global fila
    fila = []
