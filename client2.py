# -*- coding: utf-8 -*-
"""
Schema client

Un thread mi gestisce l'interfaccia, in particolare comandi di STOP e numero di richieste
Un thread gestisce tutti gli altri processi

"""
import sys
import socket 
import random

def interfaccia_col_client(client_socket):
    """
    Funzione che richiede comandi di input

    Returns
    -------
    None.

    """
    try:
        while True:
            comando = input(" Digita il comando:  ")
            # se il comando è ESC, chiudo la connessione con il server
            if comando == 'ESC':
                print("Chiusura della connessione con il server...")
                #chiudo la client socket
                client_socket.close()
                sys.exit(0)
            else:
                # Invia il comando al server (richiamo alla funzione)
                invia_richieste_al_loadbalancer(comando, client_socket)    
    except socket.error as error:
        print(f"Errore di comunicazione con il server: {error}")
        sys.exit(1)
        
    
def invia_richieste_al_loadbalancer(comando, client_socket):
    """
    Funzione che invia i comandi al loadBalancer (connessione TCP e socket) e riceve le risposte del loadBalancer

    Returns
    -------
    None.

    """
    
    # il client invia il comando di input al loadBalancer
    client_socket.send(comando.encode())
    # Riceve la risposta dal server
    data = client_socket.recv(4096)
    print(str(data, "utf-8"))
    if not data:
        print("Connessione con il server terminata.")
            
    
    

def connetti_al_loadbalancer(loadBalancer_ip, loadBalancer_port):
    """
    Funzione che crea la connessione con il load balancer (possiamo utilizzare connect oppure setsocketopt e bind)

    Returns
    -------
    None.

    """
    try:
        #creo una socket client
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # connetto il client con il loadBalancer
        client_socket.connect((loadBalancer_ip, loadBalancer_port))
        print(f"Connessione al server {loadBalancer_ip}:{loadBalancer_port} stabilita.")
        return client_socket
    except:
        print(f"Errore durante la connessione al server: {socket.error}")
        sys.exit(1)
    
    
def gestisci_richieste():
    """
    Funzione target del processo 2: crea le richieste, invia richieste, riceve richieste e le printa su terminale.
    Richiama funzioni:
        - invia comandi al server
        - crea_richieste random

    Returns
    -------
    None.

    """    
def crea_richieste_random():
    """
    Funzione che crea richieste/comandi, di carico e durata random. 
    Ad esempio, possiamo creare comandi random di calcolo; il comando scelto randomicamente verrà quindi
    inviato al loadBalancer, che a sua volta lo inoltrerà ad un server

    Returns
    -------
    None.

    """
    #selezione dei valori di carico e durata random
    carico=random.randint(1,50)
    durata=random.randint(1, 50)
    #creo due valori random A e B che servono per i calcoli
    A=random.randint(1,50)
    B=random.randint(1,50)
    #creo un dizionario di possibili richieste
    richieste={
        "somma": A+B,
        "sottrazione":A-B,
        "moltiplicazione": A*B,
        "divisione":A/B }
    #seleziono un comando in maniera casuale fra quelli presenti nel dizionario
    comando_casuale= random.choice(list(richieste.keys()))
    #creo il dizionario comando: ad ogni richiesta, associo un valore di carico e di durata, oltre che la richiesta
    #scelta in maniera randomica
    comando = {
    "carico": carico,
    "durata": durata, 
    "richiesta": comando_casuale }
    print(comando)
    return comando

    
def sconnetti_dal_load_balancer():
    """
    Funzione che chiude la connessione fra client e load balancer

    Returns
    -------
    None.

    """

def chiusura_richiesta():
    """
    Funzione che printa una notifica di chiusura della richiesta notificata dal loadbalancer

    Returns
    -------
    None.

    """


if __name__ == "__main__":
    
    # creazione della variabile globale (deve essere una lista che contiene comandi di input
    # e deve essere inizializzata anche nelle funzioni: da verificare)

    
    # Creazione del processo 1 (interfaccia)
    # Creazione del processo 2 (ricevi e invia richieste)
    
    #Avvio con start e chiudo con join i processi
    
    loadBalancer_ip= "192.168.64.1"  # Indirizzo IP del server di load balancing
    loadBalancer_port = 8888  # Porta del server
   

    client_socket = connetti_al_loadbalancer(loadBalancer_ip, loadBalancer_port)
    interfaccia_col_client(client_socket)
    crea_richieste_random()
    
    

