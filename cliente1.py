#CLIENTE COMPRADOR
from http import client
import os
import socket
import threading
import time

tipoCliente=1
IDComprador = str(20)

host = socket.gethostname()  #ip do servidor
port = 55551
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

cliente.connect((host, port))
tipo_cliente = "tipo_cliente:1,id:" + IDComprador
cliente.send(tipo_cliente.encode())


def enviar_mensagem_individual(msg):
    cliente.send(msg.encode())


def decodificar_artigo(msg):
    # os.system('cls') or None
    print("[ARTIGOS]")
    msg_sep = msg.split("/")
    for item in msg_sep:
        print(item)
    
        
def receber_msg_servidor():
    while True:
        msg = cliente.recv(1024)
        msg = msg.decode()
        msg_sep = msg.split(";")
        if msg_sep[0] == "artigo":
            decodificar_artigo(msg_sep[1])
        if msg_sep[0] == "resp":
            print(msg_sep[1])
        
           

rec_server = threading.Thread(target=receber_msg_servidor)
rec_server.start()


def start():
    while True:
        os.system('cls') or None
        enviar_mensagem_individual("listar;")
        time.sleep(1.0)
        print ('---OPCOES---' )
        print ('1 -- Dar um lance' )
        print ('2 -- Atualizar Lista' )
        option = int(input('Digite a opcao: '))

        if option == 1:
            id = input("Digite o Id do artigo: ")
            valLance = input("Digite o valor do lance: ")
            email = input("Digite seu email: ")
            lance = "lance;id:" + str(id) + ",lance:" + str(valLance) + ",idComp:" + IDComprador + ",email:" + str(email)
            enviar_mensagem_individual(lance)
            teste = input("digite para continuar")
        if option == 2:
            pass
        


start()