# -*- coding: utf-8 -*-
"""
Implementazione del load balancer
"""

def least_connection():
    pass

class LoadBalancer(object):
    
    """ Socket implementation of a load balancer.
    Flow Diagram:
    +---------------+      +-----------------------------------------+      +---------------+
    | client socket | <==> | client-side socket | server-side socket | <==> | server socket |
    |   <client>    |      |          < load balancer >              |      |    <server>   |
    +---------------+      +-----------------------------------------+      +---------------+
    Attributes:
        ip (str): virtual server's ip; client-side socket's ip
        port (int): virtual server's port; client-side socket's port
        algorithm (str): algorithm used to select a server
        flow_table (dict): mapping of client socket obj <==> server-side socket obj
        sockets (list): current connected and open socket obj
    """
    #Configurazione del load balancer
    def __init__(self):
        #indirizzo ip e porta dei server di backend
        #lista dei server attivi
        # N.B. utilizziamo una funzione che mi richiede i server presenti in quel momento, dal momento che si possono creare e distruggere
        self.servers=[]
        #Dizionario che mappa i collegamenti client - server
        self.dizionario={ }
        pass

    def creo_socket_server(self):
        #Assegna un indirizzo IP e una porta al server di load balancing, su cui ascolterà le richieste dei client.
        pass

    def accetto_connessioni(self):
        #accettazione delle connessioni del client in entrata sulla socket
        pass

    def seleziona_server(self):
        #seleziona uno dei server backend disponibili utilizzando l'algoritmo di bilanciamento del carico scelto (least connection)
        pass
    def inoltro_richieste_al_server(self):
        #inoltra la richiesta del client al server backend utilizzando una nuova connessione o una connessione esistente
        pass

    def gestione_risposte(self):
        #trasmetti la risposta al client originale che ha effettuato la richiesta
        #Puoi utilizzare la socket del client originale per inviare la risposta al client
        pass
    def gestisci_connessioni(self):
        #Gestisci le connessioni in arrivo e in uscita, monitorando le connessioni attive
        # e chiudendo eventuali connessioni inattive o problematiche
        pass

    def monitoraggio_server(self):
        #Implementa funzionalità di monitoraggio per monitorare le prestazioni
        # dei server backend e il carico sul server di load balancing
        pass

    def gestione_errori(self):
        #implementa la gestione degli errori per affrontare scenari come errori di connessione,
        # timeout, errori del server backend, ecc.
        pass

if __name__ == '__main__':
    pass