#CLIENTE VENDEDOR
import time
import os
import socket
import threading

tipoCliente=1
clienteID=10 

host = socket.gethostname()  #ip do servidor
port = 55551
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


cliente.connect((host, port))
tipo_cliente = "tipo_cliente:0,id:" + str(clienteID)
cliente.send(tipo_cliente.encode())

def receber_msg_servidor():
    while True:
        msg = cliente.recv(1024)
        msg = msg.decode()
        msg_sep = msg.split(";")
        if msg_sep[0] == "resp":
            print(msg_sep[1])


rec_server = threading.Thread(target=receber_msg_servidor)
rec_server.start()

nomeArtigo = input("Digite o nome do artigo:")
descArtigo = input("Digite a descricao do artigo:")
valorMinimo = input("Digite o lance minimo do artigo:")

artigo = "art;id:" + str(clienteID) + ",nomeArtigo:" + str(nomeArtigo) + ",descArtigo:" + str(descArtigo) + ",valorMinimo:" + str(valorMinimo)
os.system('cls') or None
cliente.send(artigo.encode())

while True:
    option = input("Digite exit para encerrar o leilão\n")
    if option == "exit":
        msg_encerrar_leilao = "close;idArt:" + str(clienteID)
        cliente.send(msg_encerrar_leilao.encode())