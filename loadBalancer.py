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
        # porta in cui si mette in ascolto il server
        self.port = 8888
        self.ip = '0.0.0.0'
        self.clients = []
        self.active_clients = []
        self.richieste = {}  # la chiave è ip del client, argomento nome richieste
        self.servers = []
        self.port_server = []

    def avvio_loadbalancer(self):
        """
        funzione che aavvia i metodi del loadbalancer, nel caso apre e chiude thread per gestire comunicazioni con client
        e server
        """
        pass
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
            data = client_socket.recv(4096)
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
        Funzione che crea la socket TCP del loadBalancer per connetterlo all'host ed ai server
        
        (da modificare)
        
        Returns
        -------
        None.
        """

        # Creazione della socket del server
        balancer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Binding della socket all'host e alla porta
        balancer_socket.bind((self.ip, self.port))
        # 10 è il backlog, ovvero il numero massimo di richieste che possono essere in attesa
        # balancer_socket.listen(10)
        print("Server di load balancing in ascolto su {}:{}".format(self.ip, self.port))

        while True:
            # Accetta le connessioni in entrata
            client_socket, client_ip = balancer_socket.accept()
            # Commento di riuscita connessione con il client
            print("Connessione accettata da {}:{}".format(client_ip[0], client_ip[1]))
            # Avvia un thread separato per gestire il client
            client_thread = threading.Thread(target=self.gestione_comunicazione_client, args=(client_socket,))
            client_thread.start()
        self.gestione_comunicazione_client(client_socket)
        
    def monitoraggio_server(self):
        """
        metodo o insieme di metodi che ricevono e salvano le informazioni dello status (numero di richieste,
        operativo o non operativo, carico computazionale solo se troviamo funzioni che ci consentono di osservarlo )di ogni sever  in tempi regolari
        """ 
        pass
    def gestione_comunicazione_server(self):
        """
        funzione che invia e distribuisce le richieste(tramite la funzione di algortimo nel nostro caso il round robin).
        manda il segnale di chiusura della richiesta, reinvia il risulatato della richiesta
        
        """

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

