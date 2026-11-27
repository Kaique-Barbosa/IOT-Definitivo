# Diário do Projeto — Miniestação Meteorológica IoT (Edge Device)

## Estado atual

* **Fase atual:** Fase 8 — Resiliência Offline, Fila em RAM e Captive Portal
* **Status:** Concluído (Escopo de Firmware da Placa Finalizado)
* **Última atualização:** 2026-10-11
* **Último commit:** feat: adiciona alternancia de simulacao de queda de Wi-Fi via Botao A (GPIO 5) para teste de fila na RAM
* **Branch atual:** development

## Objetivo do projeto

Desenvolver o firmware de uma miniestação meteorológica IoT embarcada baseada na arquitetura MVC, utilizando o Raspberry Pi Pico W na placa BitDogLab (v6.3). O dispositivo é responsável por coletar leituras dos sensores (BMP280, DHT11 e Sensor de Chuva), gerenciar resiliência offline através de fila circular na RAM, fornecer feedback visual (Display OLED e Matriz de LEDs NeoPixel 5x5), permitir configuração dinâmica de rede via Captive Portal Wi-Fi e transmitir os dados formatados em JSON para um broker MQTT.

> **Nota de Escopo:** Conforme definição de arquitetura, este repositório é estritamente dedicado ao dispositivo de borda (firmware/hardware da placa). A recepção, armazenamento persistente, processamento analítico e pipelines de Big Data serão desenvolvidos em um projeto/repositório desacoplado.

## Hardware

* Raspberry Pi Pico W
* BitDogLab (v6.3)
* BMP280 (Temperatura e Pressão atmosférica via I2C0)
* DHT11 (Temperatura e Umidade relativa via pino Digital)
* Sensor de chuva (Nível analógico de precipitação via ADC2)
* Display OLED SSD1306 128x64 (Interface I2C1)
* Matriz de LEDs NeoPixel WS2812B 5x5 (Feedback visual de fila via GP7)
* Botão A (Simulação de queda/restabelecimento de rede via GP5 com Pull-Up)

## Arquitetura de Software

Arquitetura MVC modular (Model / View / Controller):

```text
firmware/
├── config.py               # Constantes padrão, tópicos MQTT, limites
├── main.py                 # Controller principal e orquestrador do ciclo
├── credenciais.json        # Armazenamento em flash das credenciais Wi-Fi (gerado em runtime)
├── lib/
│   ├── bmp280.py           # Driver do sensor de pressão/temperatura
│   ├── ssd1306.py          # Driver gráfico do display OLED
│   └── umqtt/              # Cliente MQTT leve (umqtt.simple)
├── models/
│   ├── sensors.py          # Leitura unificada e cache dos sensores
│   └── queue_manager.py    # Fila circular FIFO na RAM
├── views/
│   ├── display.py          # Visualização no OLED SSD1306
│   └── led_matrix.py       # Medidor de capacidade na Matriz NeoPixel 5x5
└── controllers/
    ├── connectivity.py     # Gestão de Wi-Fi, MQTT e simulação
    └── portal.py           # Captive Portal (Access Point + Servidor HTTP embutido)
```

## GPIOs e Conexões

| Componente      | Interface | GPIO        | Função / Descrição | Status     |
| --------------- | --------- | ----------- | ------------------ | ---------- |
| BMP280          | I2C0      | GP16 / GP17 | Dados / Clock      | Confirmado |
| DHT11           | Digital   | GP18        | Barramento 1-Wire  | Confirmado |
| Sensor de chuva | ADC2      | GP28        | Leitura Analógica  | Confirmado |
| OLED SSD1306    | I2C1      | GP14 / GP15 | Dados / Clock      | Confirmado |
| Matriz WS2812B  | NeoPixel  | GP7         | Sinal Digital (25 LEDs) | Confirmado |
| Botão A         | Digital   | GP5         | Simulação Queda (Pull-Up) | Confirmado |

## Documentação Utilizada

* `AgentesRegras.md`: Define regras de fluxo, ensino e comportamento do agente.
* `datasheet do bitdoglab v6.3.md`: Mapeamento de pinos e periféricos da placa-mãe.
* Repositório `BitDogLab-docs`: Exemplos práticos e esquemáticos da placa.

## Fases do Projeto

### Fase 0 — Reconhecimento e Planejamento
* Status: Concluída
* Definição de pinout, arquitetura MVC e formato de payload JSON.

### Fase 1 — Preparação do Ambiente
* Status: Concluída
* Configuração do MicroPico, VS Code e repositório Git com branches `main` e `development`.

### Fase 2 — Testes Individuais dos Sensores
* Status: Concluída
* Validação individual do DHT11, BMP280 e sensor de chuva.

### Fase 3 — Integração dos Sensores e Display OLED
* Status: Concluída
* Camadas `models/sensors.py` e `views/display.py` unificadas com coleta de lixo periódica (`gc.collect()`).

### Fase 4 — Gerenciamento da Memória RAM e Matriz de LEDs
* Status: Concluída
* Implementação da fila FIFO circular (`queue_manager.py`) e visualização na matriz NeoPixel 5x5 de baixo para cima (`led_matrix.py`).

### Fase 5 — Protocolo e Cliente MQTT
* Status: Concluída
* Integração do driver `umqtt.simple` no firmware com suporte a QoS 0 e publicação formatada em JSON.

### Fase 6 — Conexão com Broker Externo
* Status: Concluída
* Configuração do cliente para publicação em broker público (`broker.hivemq.com`).

### Fase 7 — Resiliência de Publicação e Descarregamento em Rajadas
* Status: Concluída
* Lógica de envio automático das mensagens pendentes na fila de RAM em lotes de até 5 registros por ciclo ao restaurar conectividade.

### Fase 8 — Captive Portal Autônomo e Simulação de Falhas
* Status: Concluída
* Implementação do modo Access Point (`portal.py`) para configuração de credenciais Wi-Fi pelo celular sem alterar código.
* Validação de credenciais na memória RAM antes de gravar no flash do dispositivo.
* Mecanismo de alternância de simulação de queda de rede acionado via Botão A (GPIO 5).

---

## Histórico de Marcos

* **2026-09-30:** Definição da Estrutura do Payload, conclusão da Fase 0 e transição para Fase 1. Inicialização do Git e criação de branches.
* **2026-09-30:** Conclusão das Fases 1, 2 e 3. Implementação da arquitetura MVC. Testes de sensores (DHT11, BMP280, Chuva) validados. Criação de cache e view do OLED.
* **2026-10-02:** Resolução de memory leak via `gc.collect()`. Implementação da Fila em RAM FIFO e barra de progresso na Matriz NeoPixel 5x5. Instalação da biblioteca `umqtt.simple`.
* **2026-10-11:** Implementação do Captive Portal autônomo (AP + Servidor HTTP na porta 80). Validação dinâmica de credenciais sem reboot. Criação do modo de simulação de queda de rede via Botão A (GPIO 5). Fechamento do escopo de firmware da placa.
