import socket
import threading
import time



host = socket.gethostname()
port = 55551

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind((host, port))
serv.listen(5)


artigos_inventario = []
artigos_encerrados = []
conexoes_vendedor = []
conexoes_comprador = []


def listar_conexoes_vendedor():
    global conexoes_vendedor
    for item in conexoes_vendedor:
        print(item)

def listar_conexoes_comprador():
    global conexoes_comprador
    for item in conexoes_comprador:
        print(item)

def listar_leilao():
    for item in artigos_inventario:
        print(item)


#########################################################


def enviar_msg(msg, conn):
    conn.send(msg.encode())


def codificar_artigos():
    msg = "artigo;"
    for item in artigos_inventario:
        msg += ("id:" + str(item['id']) + "," + 
                "nome:" + str(item['nome']) + "," +
                "descricao:" + str(item['descricao']) + "," +
                "valorMinimo:" + str(item['valorMinimo']) +  "," +
                "MaiorLance:"+ str(item['maiorLance']) + "/" )

    return msg


def decodificar_tipo_cliente(msg):
    msg_sep = msg.split(":")
    tipoCliente = msg_sep[1]
    return int(tipoCliente)

def decodificar_id(msg):
    msg_sep = msg.split(":")
    return msg_sep[1]


def maior_lance(arlances):
    maior = 0
    id= ""
    if not arlances:
        return maior
    else:
        for item in arlances:
            if int(item['lance'])>maior:
                maior=int(item['lance'])
                id = item['idComp']

    retorno = {
        "maiorLance": maior,
        "idMaiorLance": id
    }

        

    return retorno

def salvar_lance(msg,conn_comprador):
    msg_sep = msg.split(",")
    preid = msg_sep[0].split(":")
    prelance = msg_sep[1].split(":")
    preIdComprador = msg_sep[2].split(":")
    preEmail = msg_sep[3].split(":")
    artigo_n_encontrado = True

    id = preid[1]
    lance = int(prelance[1])
    IdComprador = preIdComprador[1]
    email = preEmail[1]

    lance_id = {
        "lance": lance,
        "idComp": IdComprador,
        "email": email
    }
        

    for item in artigos_inventario:
        if item['id'] == str(id):
            artigo_n_encontrado = False
            conn_vendedor = item['conexao']

            if lance < int(item['valorMinimo']):
                enviar_msg("resp;Seu lance foi abaixo do valor mínimo", conn_comprador)
            else:
                item['lances'].append(lance_id)
                mensagem_retorno_vendedor = (f"resp;Um Lance de {lance} foi dado no artigo {item['nome']}")
                enviar_msg(mensagem_retorno_vendedor, conn_vendedor)
                enviar_msg("resp;Seu lance foi salvo com SUCESSO.", conn_comprador)
                maiorLance = maior_lance(item['lances'])
                if maiorLance['maiorLance'] == 0:
                    item['maiorLance'] = str(lance)
                else:
                    item['maiorLance'] = str(maiorLance['maiorLance'])

    if artigo_n_encontrado:
        enviar_msg("resp; Esse artigo nao existe ou o leilao ja foi encerrado.", conn_comprador)

def salvar_artigo(msg, conn):
    global artigos_inventario

    msg_sep = msg.split(",")
    id = msg_sep[0].split(":")[1]
    nomeArtigo = msg_sep[1].split(":")[1]
    descArtigo = msg_sep[2].split(":")[1]
    valor = msg_sep[3].split(":")[1]
    lances = []
    artigo = {"id": id,
            "nome": nomeArtigo,
            "descricao": descArtigo,
            "valorMinimo": valor,
            "lances": lances,
            "maiorLance": "",
            "conexao": conn}
    artigos_inventario.append(artigo)

def vencedor(arrlances):
    maior = 0
    vencedor_id = ""
    vencedor_email = ""
    
    for item in arrlances:
        if int(item['lance'])>maior:
            maior = int(item['lance'])

            vencedor_id = item['idComp']
            vencedor_email = item['email']
            vencedor_lance = item['lance']

    for usr in conexoes_comprador:
        if usr['id'] == vencedor_id:
            vencedor_conn = usr['conn']
    
    vencedor = {
        "venc_id": vencedor_id,
        "venc_email": vencedor_email,
        "venc_conn": vencedor_conn,
        "venc_lance": vencedor_lance
    }
    return vencedor


def encerrar_leilao(msg, conn_vendedor):
    msg_sep = msg.split(":")
    id = msg_sep[1]
    
    for item in artigos_inventario:
        if item['id'] == id:
            if item['lances']:
                print(item['lances'])
                vencedor_final = vencedor(item['lances'])
                msg_final = (f"resp;Leilao encerrado - Email Vencedor: {vencedor_final['venc_email']}, Lance: {vencedor_final['venc_lance']}")
                        
                enviar_msg(msg_final, conn_vendedor)
            
                artigos_encerrados.append(item)
                artigos_inventario.remove(item)
            else:
                enviar_msg("resp;Não houve lances neste artigo.", conn_vendedor)
                artigos_encerrados.append(item)
                artigos_inventario.remove(item)



#########################################################



def escutar_cliente_vendedor(conn):
    while True:
        msg = conn.recv(1024)
        msg = msg.decode()
        mensagem_sep = msg.split(";")
        if mensagem_sep[0] == "art":
            salvar_artigo(mensagem_sep[1],conn)
            enviar_msg("resp;Seu artigo foi salvo com SUCESSO. O leilão acaba de ser iniciao.", conn)
        elif mensagem_sep[0] == "close":
            encerrar_leilao(mensagem_sep[1], conn)
        

def escutar_cliente_comprador(conn):
    while True:
        msg = conn.recv(1024)
        msg = msg.decode()
        mensagem_sep = msg.split(";")
        if mensagem_sep[0] == "listar":
            artigos = codificar_artigos()
            enviar_msg(artigos, conn)
        elif mensagem_sep[0] == "lance":
            salvar_lance(mensagem_sep[1], conn)


def iniciar_srv():
    global conexoes_vendedor
    global conexoes_comprador
    while True:
        conn, addr = serv.accept()
        identificacao = conn.recv(1024)
        identificacao = identificacao.decode()
        identificacao_sep = identificacao.split(",")
        tipo_cliente = decodificar_tipo_cliente(identificacao_sep[0])
        id = decodificar_id(identificacao_sep[1])

        id_conn = {
            "id":id,
            "conn": conn
        }

        if tipo_cliente == 0:
            conexoes_vendedor.append(id_conn)
            client = threading.Thread(target=escutar_cliente_vendedor, args={conn})
            client.start()
        elif tipo_cliente == 1:
            conexoes_comprador.append(id_conn)
            client = threading.Thread(target=escutar_cliente_comprador, args={conn})
            client.start()
   



def start():    
    while True:
        print ('1 -- Listar itens no leilão' )
        print ('2 -- Listar conexões comprador' )
        print ('3 -- Listar conexões vendedor' )
        print ('4 -- Exit' )   
        start = threading.Thread(target = iniciar_srv)
        start.start()        
        option = int(input('Digite a opcao: '))

        if option == 1:
            listar_leilao()
        elif option == 2:
            listar_conexoes_comprador()
        elif option == 3:
            listar_conexoes_vendedor()


start()