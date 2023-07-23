# -*- coding: utf-8 -*-
"""
Implementazione del load balancer
"""
import threading
import socket


def round_robin_method():
    pass



class LoadBalancer(object):

    
    def __init__(self):
        """
        Costruttore della classe loadBalancer
        """
        #porta in cui si mette in ascolto il server
        self.port=8888


    def gestione_comunicazione_client(self,client_socket):
        """
        Funzione che gestisce la comunicazione con il client:
            il server riceve i dati dal client e invia una risposta di avvenuta connessione;
            in seguito invierà il comando ad un server per elaborare la richiesta 
        Returns
        -------
        None.
        """
        while True:
            # il loadBalancer riceve i dati dal client
            data=client_socket.recv(4096)
            if not data:
                break
            # Elabora la richiesta del client
            risposta = " Il server di load balancer ha ricevuto il comando e lo inoltra ad un server"
            # il loadBalancer risponde al client per l'avvenuta connessione
            client_socket.send(risposta.encode())
            #DEVO CHIAMARE LA FUNZIONE CHE INOLTRA LA RICHIESTA AD UN SERVER CON MECCANISMO ROUND ROBIN
        client_socket.close()
        


    def creazione_socket_loadBalancer(self):
        """
        Funzione che crea la socket TCP del loadBalancer per connetterlo all'host
        
        Returns
        -------
        None.
        """
        host= "" #il server è in ascolto su tutte le interfacce disponibili dell'host
        port=self.port
        
        # Creazione della socket del server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        
        #10 è il backlog, ovvero il numero massimo di richieste che possono essere in attesa
        server_socket.listen(10)
        print("Server di load balancing in ascolto su {}:{}".format(host, port))

        while True:
            client_socket, client_ip = server_socket.accept()
            print("Connessione accettata da {}:{}".format(client_ip[0], client_ip[1]))
            # Avvia un thread separato per gestire il client
            client_thread = threading.Thread(target=self.gestione_comunicazione_client, args=(client_socket,))
            client_thread.start()
        self.gestione_comunicazione_client(client_socket)
        
        


if __name__ =='__main__':
    
    load_balancer=LoadBalancer()
    load_balancer.creazione_socket_loadBalancer()
    








    #def attiva_server():
    #pass

    # def accetto_connessioni(self):
    #     #accettazione delle connessioni del client in entrata sulla socket
    #     pass

    # def seleziona_server(self):
    #     #seleziona uno dei server backend disponibili utilizzando l'algoritmo di bilanciamento del carico scelto (least connection)
    #     pass
    # def inoltro_richieste_al_server(self):
    #     #inoltra la richiesta del client al server backend utilizzando una nuova connessione o una connessione esistente
    #     pass

    # def gestione_risposte(self):
    #     #trasmetti la risposta al client originale che ha effettuato la richiesta
    #     #Puoi utilizzare la socket del client originale per inviare la risposta al client
    #     pass
    # def gestisci_connessioni(self):
    #     #Gestisci le connessioni in arrivo e in uscita, monitorando le connessioni attive
    #     # e chiudendo eventuali connessioni inattive o problematiche
    #     pass

    # def monitoraggio_server(self):
    #     #Implementa funzionalità di monitoraggio per monitorare le prestazioni
    #     # dei server backend e il carico sul server di load balancing
    #     pass

    # def gestione_errori(self):
    #     #implementa la gestione degli errori per affrontare scenari come errori di connessione,
    #     # timeout, errori del server backend, ecc.
    #     pass

