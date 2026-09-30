# Diário do Projeto — Estação Meteorológica

## Estado atual

* **Fase atual:** Fase 1 — Preparação do ambiente
* **Status:** Em andamento
* **Última atualização:** 2026-09-30
* **Último commit:** chore: commit inicial com estrutura completa MVC do firmware
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
├── main.py
├── models/
│   └── sensors.py
├── views/
│   ├── display.py
│   └── led_matrix.py
└── controllers/
    └── .gitkeep
```

## GPIOs e conexões

| Componente      | Interface | GPIO        | Status                |
| --------------- | --------- | ----------- | --------------------- |
| BMP280          | I2C0      | GP16 / GP17 | Confirmado            |
| DHT11           | Digital   | GP18        | Confirmado            |
| Sensor de chuva | ADC2      | GP28        | Confirmado (Jumper JP1 em ANA-IN) |

## Documentação utilizada

* `AgentesRegras.md`: Define regras de fluxo, ensino e comportamento do agente.
* `datasheet do bitdoglab v6.3.md`: Mapeamento de pinos e periféricos da placa-mãe.
* Repositório `BitDogLab-docs`: Biblioteca de exemplos, códigos básicos e esquemas.

## Fases do projeto

### Fase 0 — Reconhecimento e planejamento
* Status: Concluída

### Fase 1 — Preparação do ambiente
* Status: Em andamento

### Fase 2 — Testes individuais dos sensores
* Status: Não iniciada

### Fase 3 — Integração dos sensores
* Status: Não iniciada

### Fase 4 — Gerenciamento da memória RAM
* Status: Não iniciada (Adiada para versão futura focada em resiliência offline)

### Fase 5 — Fundamentos do MQTT
* Status: Não iniciada

### Fase 6 — Primeiro teste MQTT
* Status: Não iniciada

### Fase 7 — Integração do Pico W com MQTT
* Status: Não iniciada

### Fase 8 — Mecanismo de armazenamento durante desconexão
* Status: Não iniciada

### Fase 9 — Recepção e Preparação para Big Data
* Status: Não iniciada

## Decisões técnicas

### DECISÃO — Adoção do Git e Github
* **Data:** 2026-09-30
* **Decisão:** Implementar controle de versionamento Git e sincronizar com repositório remoto.
* **Motivo:** Preservar a história técnica do código e ter fluxo seguro de branches (main e development).

### DECISÃO — Payload, Taxa de Atualização e MQTT
* **Data:** 2026-09-30
* **Decisão:** 
  - Frequência de leitura em 1Hz (1 segundo) para respeitar o limite físico do sensor DHT11.
  - Fusão de Sensores: Será calculada a média térmica entre as leituras do DHT11 e do BMP280.
  - Payload legível: As chaves do JSON utilizarão palavras claras (`temperatura`, `umidade`, etc) em vez de letras isoladas, priorizando a legibilidade para a análise em Big Data.
  - Fluxo inicial: Envio imediato via protocolo MQTT (com QoS 0 - mais leve) para simplificar a versão 1.0.
* **Formato do Payload Definido:**
  ```json
  {
    "temperatura": 28.4,
    "umidade": 60.2,
    "pressao": 1012.5,
    "chuva": 45000
  }
  ```

## Testes realizados

Nenhum teste foi realizado até o momento.

## Pendências

* **[PENDENTE] - Validação do Ambiente:** Realizar teste mínimo de execução (Hello World/Blink) na placa para iniciar a Fase 1.

## Histórico

* **2026-09-30:** Definição da Estrutura do Payload, Taxa de 1Hz, conclusão da Fase 0 e transição para Fase 1.
* **2026-09-30:** Criação do DIÁRIO_DO_PROJETO, inicialização Git, criação branches main e development.
