# -*- coding: utf-8 -*-
"""
Implementazione del client 1
"""
import socket
import sys

#Stabilisco una connessione
#creo una socket client

def stabilisco_connessione(server_address, server_port):
    """
    Questa funzione crea una client socket e stabilisce una connessione con il server indicato dall'address
    e dalla porta in input

    Args:
        server_address: string
        server_port: int

    Returns:

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


#comunico con il server
def comunicazione():
    #invio dati: funzione send
    #ricevo dati: funzione recv
    pass

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
    server_address = "192.168.64.1"  # Indirizzo IP del server
    server_port = 8888  # Porta del server

    # Stabilisce la connessione con il server
    client_socket = stabilisco_connessione(server_address, server_port)

