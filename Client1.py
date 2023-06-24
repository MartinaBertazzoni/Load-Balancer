# -*- coding: utf-8 -*-
"""
Implementazione del client 1
"""
import socket
import sys

#Stabilisco una connessione
#creo una socket client

#comunico con il server
def comunico_con_il_server(client_socket):
    """
    Funzione che invia comandi al server (load balancer)
    
    """
    try:
        while True:
            #Ottengo l'input dall'utente
            comando = input(" Digita il comando:  ")
            # se il comando è ESC, chiudo la connessione con il server
            if comando == 'ESC':
                print("Chiusura della connessione con il server...")
                #chiudo la client socket
                client_socket.close()
                sys.exit(0)
            else:
                # Invia il comando al server
                client_socket.send(comando.encode())
                # Riceve la risposta dal server
                data = client_socket.recv(4096)
                print(str(data, "utf-8"))
                if not data:
                    print("Connessione con il server terminata.")
                    break
    except socket.error as error:
        print(f"Errore di comunicazione con il server: {error}")
        sys.exit(1)

def stabilisco_connessione(server_address, server_port):
    """
    Questa funzione crea una client socket e stabilisce una connessione con il server indicato dall'address
    e dalla porta in input
    
    Args:
        server_address: string
        server_port: int
    """
    try:
        #creo una socket client
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Stabilisce la connessione con il server
        client_socket.connect((server_address, server_port))
        print(f"Connessione al server {server_address}:{server_port} stabilita.")
        return client_socket
    except:
        print(f"Errore durante la connessione al server: {socket.error}")
        sys.exit(1)
    


def elabora_dati():
    #elaboro i dati ricevuti dal server
    pass

def gestisci_input():
    #se ho bisogno di input dall'utente, li richiedo
    pass


def chiudi_connessione():
    #funzione close per chiudere la socket
    pass


if __name__ == "__main__":
    
    server_address = "192.168.64.1"  # Indirizzo IP del server di load balancing
    server_port = 8888  # Porta del server

    # Stabilisce la connessione con il server
    client_socket = stabilisco_connessione(server_address, server_port)
    comunico_con_il_server(client_socket)

