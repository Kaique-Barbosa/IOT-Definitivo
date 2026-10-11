import network
import socket
import time

# ===== CONFIGURAÇÃO DO ACCESS POINT =====
AP_SSID = "EstacaoIoT-Config"
AP_PASS = "12345678"

ap = None

# ===== PÁGINA HTML DO PORTAL =====
# Formulário simples servido pelo mini servidor HTTP embutido.
# Não usa bibliotecas externas — apenas socket nativo do MicroPython.
PAGINA_HTML = b"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Estacao IoT - Configurar Wi-Fi</title>
  <style>
    body { font-family: sans-serif; max-width: 360px; margin: 40px auto; padding: 20px; background: #f4f4f4; }
    h2 { color: #333; text-align: center; }
    p { color: #555; font-size: 14px; }
    input { width: 100%; padding: 10px; margin: 8px 0; box-sizing: border-box; border-radius: 6px; border: 1px solid #ccc; font-size: 15px; }
    button { width: 100%; padding: 12px; background: #4CAF50; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; margin-top: 10px; }
    button:hover { background: #45a049; }
  </style>
</head>
<body>
  <h2>&#128225; Estacao IoT</h2>
  <p>A placa nao conseguiu conectar ao Wi-Fi. Informe a rede que ela deve usar:</p>
  <form method="POST" action="/salvar">
    <label>Nome da rede (SSID):</label>
    <input type="text" name="ssid" placeholder="Ex: MinhaRede" required>
    <label>Senha:</label>
    <input type="password" name="senha" placeholder="Senha do Wi-Fi" required>
    <button type="submit">Salvar e Conectar</button>
  </form>
</body>
</html>"""

PAGINA_SUCESSO = b"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Salvo!</title>
  <style>
    body { font-family: sans-serif; max-width: 360px; margin: 40px auto; padding: 20px; text-align: center; }
    h2 { color: #4CAF50; }
    p { color: #555; }
  </style>
</head>
<body>
  <h2>&#10003; Credenciais Salvas!</h2>
  <p>A placa vai tentar se conectar agora.</p>
  <p>Se a conexao falhar, ela voltara ao modo portal.</p>
  <p>Pode fechar esta pagina.</p>
</body>
</html>"""


def _url_decode(texto):
    """
    Decodifica caracteres especiais de URLs (ex: '+' vira espaço, '%XX' vira o char).
    Necessário para ler corretamente senhas com caracteres especiais.
    """
    texto = texto.replace("+", " ")
    resultado = ""
    i = 0
    while i < len(texto):
        if texto[i] == "%" and i + 2 < len(texto):
            try:
                resultado += chr(int(texto[i+1:i+3], 16))
                i += 3
            except:
                resultado += texto[i]
                i += 1
        else:
            resultado += texto[i]
            i += 1
    return resultado


def _extrair_form(body):
    """
    Extrai os campos 'ssid' e 'senha' do corpo de uma requisição HTTP POST.
    Ex: "ssid=MinhaRede&senha=123456" → {'ssid': 'MinhaRede', 'senha': '123456'}
    """
    dados = {}
    for par in body.split("&"):
        if "=" in par:
            chave, valor = par.split("=", 1)
            dados[_url_decode(chave)] = _url_decode(valor)
    return dados


def ativar_ap():
    """
    Ativa o modo Access Point no Pico W.
    Retorna o IP do AP (geralmente '192.168.4.1').
    
    Nota: o AP deve ser ativado (active=True) antes de configurar o essid.
    Não especificamos parâmetro de segurança — o padrão é rede aberta.
    """
    global ap
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    time.sleep(0.5)

    # Ativa o AP antes de configurar (comportamento correto para o CYW43439)
    ap.active(True)
    time.sleep(0.5)

    # Tenta configurar WPA2 — com fallback para diagnosticar o erro exato
    try:
        ap.config(essid=AP_SSID, password=AP_PASS, security=7)
        print("[Portal] AP configurado com essid + password + security=7")
    except Exception as e1:
        print("[Portal] Falha com security=7:", e1)
        try:
            # Alguns firmwares usam 'ssid' e 'key' ao invés de 'essid' e 'password'
            ap.config(ssid=AP_SSID, key=AP_PASS, security=4)
            print("[Portal] AP configurado com ssid + key + security=4")
        except Exception as e2:
            print("[Portal] Falha com key/ssid:", e2)
            try:
                # Última tentativa: só o nome, sem senha
                ap.config(essid=AP_SSID)
                print("[Portal] AP configurado SEM senha (fallback)")
            except Exception as e3:
                print("[Portal] Falha total no ap.config():", e3)

    # Aguarda o AP ficar completamente ativo
    timeout = 10
    while not ap.active() and timeout > 0:
        time.sleep(0.5)
        timeout -= 1

    ip = ap.ifconfig()[0]
    print(f"[Portal] AP '{AP_SSID}' ativo! Acesse: http://{ip}")
    return ip


def desativar_ap():
    """Encerra o modo Access Point."""
    global ap
    if ap is not None:
        ap.active(False)
        ap = None
        print("[Portal] Access Point desativado.")


def aguardar_configuracao():
    """
    Sobe um servidor HTTP mínimo na porta 80 e aguarda o usuário
    submeter o formulário com SSID e senha da nova rede.
    Retorna um dicionário {'ssid': '...', 'senha': '...'} quando receber o POST.
    Fica em loop até receber as credenciais.
    """
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(("0.0.0.0", 80))
    servidor.listen(1)
    print("[Portal] Servidor HTTP aguardando na porta 80...")

    credenciais = None

    while credenciais is None:
        try:
            conn, addr = servidor.accept()
            print(f"[Portal] Conexão de {addr}")

            # Lê a requisição HTTP (até 2048 bytes)
            requisicao = conn.recv(2048).decode("utf-8", "ignore")

            if "POST /salvar" in requisicao:
                # Extrai o corpo do POST (após a linha em branco dos headers)
                if "\r\n\r\n" in requisicao:
                    body = requisicao.split("\r\n\r\n", 1)[1].strip()
                else:
                    body = ""

                dados = _extrair_form(body)
                ssid = dados.get("ssid", "").strip()
                senha = dados.get("senha", "").strip()

                if ssid:
                    # Responde com página de sucesso
                    resposta = (
                        b"HTTP/1.1 200 OK\r\n"
                        b"Content-Type: text/html; charset=utf-8\r\n"
                        b"Connection: close\r\n\r\n"
                    ) + PAGINA_SUCESSO
                    conn.send(resposta)
                    conn.close()
                    credenciais = {"ssid": ssid, "senha": senha}
                    print(f"[Portal] Credenciais recebidas: SSID='{ssid}'")
                else:
                    # SSID vazio: devolve o formulário com mensagem de erro
                    conn.send(
                        b"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nConnection: close\r\n\r\n"
                        + PAGINA_HTML
                    )
                    conn.close()
            else:
                # GET ou qualquer outra rota: serve o formulário principal
                conn.send(
                    b"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nConnection: close\r\n\r\n"
                    + PAGINA_HTML
                )
                conn.close()

        except Exception as e:
            print("[Portal] Erro no servidor HTTP:", e)

    servidor.close()
    return credenciais

