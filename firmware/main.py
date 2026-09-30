import time

print("--- Iniciando a Miniestacao Meteorologica IoT ---")
print("Arquitetura MVC criada com sucesso!")

def loop():
    while True:
        # No futuro, aqui chamaremos:
        # dados = sensors.ler_todos()
        # display.atualizar(dados)
        # queue_manager.verificar_conexao_e_salvar(dados)
        print("Loop principal rodando... (1 segundo)")
        time.sleep(1)

if __name__ == "__main__":
    loop()

