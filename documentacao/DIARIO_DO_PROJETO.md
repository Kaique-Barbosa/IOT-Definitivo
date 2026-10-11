# Diário do Projeto — Estação Meteorológica

## Estado atual

* **Fase atual:** Fase 5 — Fundamentos do MQTT (Preparação para Servidor)
* **Status:** Em andamento
* **Última atualização:** 2026-10-02
* **Último commit:** feat: implementa Fase 4 com fila na RAM, Matriz de LEDs e base MQTT
* **Branch atual:** development

## Objetivo do projeto

Desenvolver uma miniestação meteorológica IoT baseada na arquitetura MVC utilizando Raspberry Pi Pico W e a placa BitDogLab, coletando dados de sensores (BMP280, DHT11, Sensor de Chuva), e enviando dados para um servidor via MQTT.

## Hardware

* Raspberry Pi Pico W
* BitDogLab (v6.3)
* BMP280 (Temperatura e Pressão)
* DHT11 (Temperatura e Umidade)
* Sensor de chuva (Nível de precipitação/umidade analógico)

## Arquitetura

Arquitetura MVC (Model / View / Controller).

Estrutura atual:
```text
firmware/
├── config.py
├── main.py
├── lib/
│   ├── bmp280.py
│   ├── ssd1306.py
│   └── umqtt/
├── models/
│   ├── sensors.py
│   └── queue_manager.py
├── views/
│   ├── display.py
│   └── led_matrix.py
└── controllers/
    └── connectivity.py
```

## GPIOs e conexões

| Componente      | Interface | GPIO        | Status                |
| --------------- | --------- | ----------- | --------------------- |
| BMP280          | I2C0      | GP16 / GP17 | Confirmado            |
| DHT11           | Digital   | GP18        | Confirmado            |
| Sensor de chuva | ADC2      | GP28        | Confirmado            |
| OLED SSD1306    | I2C1      | GP14 / GP15 | Confirmado            |
| Matriz WS2812B  | NeoPixel  | GP7         | Confirmado            |

## Documentação utilizada

* `AgentesRegras.md`: Define regras de fluxo, ensino e comportamento do agente.
* `datasheet do bitdoglab v6.3.md`: Mapeamento de pinos e periféricos da placa-mãe.
* Repositório `BitDogLab-docs`: Biblioteca de exemplos, códigos básicos e esquemas.

## Fases do projeto

### Fase 0 — Reconhecimento e planejamento
* Status: Concluída

### Fase 1 — Preparação do ambiente
* Status: Concluída

### Fase 2 — Testes individuais dos sensores
* Status: Concluída

### Fase 3 — Integração dos sensores e OLED
* Status: Concluída

### Fase 4 — Gerenciamento da memória RAM, Matriz de LEDs e base MQTT
* Status: Concluída

### Fase 5/6 — Configuração do Servidor MQTT Externo
* Status: Não iniciada

### Fase 7 — Integração do Pico W com MQTT (Envio Real)
* Status: Não iniciada

### Fase 8 — Refinamento do mecanismo de armazenamento offline
* Status: Parcialmente Concluída (Fila na RAM e Matriz visuais prontos)

### Fase 9 — Recepção e Preparação para Big Data
* Status: Não iniciada

## Histórico

* **2026-09-30:** Definição da Estrutura do Payload, conclusão da Fase 0, transição para Fase 1. Inicialização Git, criação branches.
* **2026-09-30:** Conclusão das Fases 1, 2 e 3. Implementação MVC. Testes de sensores (DHT11, BMP280, Chuva) validados. Criação de Cache para o DHT11 e View OLED.
* **2026-10-02:** Correção de memory leak no MicroPython usando `gc.collect()`. Implementação concluída da Fase 4: `queue_manager.py` (Fila RAM FIFO de 300 posições), `led_matrix.py` (Barra de progresso NeoPixel), e `connectivity.py` (Base MQTT QoS 0 via `umqtt.simple`). O sistema agora armazena os dados offline e exibe progresso na Matriz de LEDs. Instalação manual da lib `umqtt` no firmware.

