# -*- coding: utf-8 -*-
"""
Implementazione del server 1 
"""
import socket
import threading

def gestisci_connessione(client_socket, client_address):
    """
    # Logica per gestire la connessione dal load balancer
    # N.B. Implementa qui la logica per ricevere e gestire le richieste
    # inviate dal load balancer al server

    Parameters
    ----------
    client_socket
    client_address 

    Returns
    -------
    None.

    """
    while True:
        data = client_socket.recv(4096)
        if not data:
            break
        # Esegui le operazioni richieste dal load balancer
        # e invia le risposte al load balancer
        response = "Risposta del server"
        client_socket.sendall(response.encode())
    
    client_socket.close()
    
def start_server(host, port):
    """
    Funzione che crea la socket del server e lo mette in ascolto sulla porta
    del load balancer

    Parameters
    ----------
    host 
    port 
        
    Returns
    -------
    None.
    """
    # Creo la socket del server 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Collego la socket del server all'IP e alla porta dell'host (quindi del Load Balancer)
    server_socket.bind((host, port))
    # Il server è in ascolto; può avere massimo 10 richieste in attesa
    server_socket.listen()
    print(f"Server in ascolto su {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connessione accettata da {client_address[0]}:{client_address[1]}")
        
        # Avvia un thread separato per gestire la connessione
        connection_thread = threading.Thread(target=gestisci_connessione, args=(client_socket, client_address))
        connection_thread.start()

host ="192.168.64.1"
port = 8888

start_server(host, port)

