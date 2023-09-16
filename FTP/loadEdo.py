import threading
import socket
import logging
from pynput import keyboard  # Import pynput library
import sys
import multiprocessing
import time
import subprocess

class LoadBalancer:
    """
    Classe che implementa il load balancer
    """

    def _init_(self):
        """
        Costruttore della classe
        """
        # variabile che ospiterà la socket del load balancer
        self.balancer_socket = None
        # indirizzo e porta del load balancer
        self.ADDRESS = ("127.0.0.1", 60003)
        # clients
        self.CLIENTS = []
        # clients attivi
        self.ACTIVE_CLIENTS = []
        # lista degli indirizzi dei server a cui il LB si può interfacciare
        self.SERVERS = ["127.0.0.1", "127.0.0.1", "127.0.0.1"]
        # lista delle porte dei server a cui il LB si può interfacciare
        self.PORTS = [5007, 5008, 5009]
        # indice del server a cui il LB si sta interfacciando
        self.CURRENT_SERVER_INDEX = 0
        # indice della porta del server a cui il LB si sta interfacciando
        self.CURRENT_SERVER_PORT_INDEX = 0
        # lista che contiene le flag per il monitoraggio dei server
        self.SERVER_FLAGS = [False] * len(self.SERVERS)
        # lista che contiene le flag per il monitoraggio del sovraccarico dei server
        self.SERVER_SOVRACCARICO_FLAGS = [False] * len(self.SERVERS)
        # lista che contiene i processi attivi
        self.PROCESSI_ATTIVI = []



    def socket_loadBalancer(self):
        """
        Funzione che crea la socket del load balancer
        Returns
        -------
        """
        try:
            print("[STARTING] Il load balancer sta partendo.")
            # Creazione della socket del server
            self.balancer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Binding della socket all'host e alla porta
            self.balancer_socket.bind(self.ADDRESS)
            self.balancer_socket.listen()
            time.sleep(0.5)
            print("[LISTENING] Server di load balancing in ascolto su {}:{}".format(self.ADDRESS[0], self.ADDRESS[1]))
            threading.Thread(target=self.monitoraggio_status_server()).start()
        except:
            print("[ERROR] Errore nella creazione della socket del load balancer")
            print("Il load balancer si chiude")
            sys.exit()


    def accettazione_client(self):
        """
        Funzione che accetta i client in entrata
        Returns
        -------
        """
        try:
            while True:
                # accetto le connessioni in entrata
                client_socket, client_address = self.balancer_socket.accept()
                print(f"[NEW CONNECTION] {client_address} connesso al load balancer.")
                # aggiungo il client alla lista dei client
                self.CLIENTS.append(client_socket)
        except:
            print("[ERROR] Errore nella connessione con il client")
            print("Il load balancer si chiude")
            sys.exit()


    def ricevi_dai_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                message = data.decode("utf-8")
                if message == "exit":
                    print(f"[DISCONNECTION] {client_socket} si è disconnesso dal load balancer")
                    exit_message = "Disconnessione dal load balancer"
                    # invio il messaggio di disconnessione al client
                    self.balancer_socket.send(exit_message.encode('utf-8'))
                    # chiudo la socket del client
                    client_socket.close()
                    # termino il thread
                    sys.exit()
                else:
                    memoria = []
                    # salvo il nome del file ricevuto dal client in una variabile specifica
                    nome_file = data
                    # salvo il nome del file nella memoria
                    memoria.append(nome_file)
                    # ricevo il contenuto del file dal client
                    contenuto_file = client_socket.recv(1024)
                    # salvo il contenuto del file nella memoria
                    memoria.append(contenuto_file)
                    # invio tutto ciò che ho ricevuto al server
                    for dato in memoria:
                        self.invia_ai_server(dato)
                        time.sleep(0.2)
                    # svuoto la memoria per il prossimo file
                    memoria.clear()
                    # messaggio di conferma
                    print("[OK] File ricevuto dal client e inviato al server")
                    # invio il messaggio di conferma al client
                    self.balancer_socket.send("[OK] File ricevuto dal client e inviato al server".encode('utf-8'))
        except:
            print("[ERROR] Errore nella ricezione del file dal client")
            self.balancer_socket.send("[ERROR] Errore nella ricezione del file".encode('utf-8'))



    def invia_ai_server(self, dato):
        """
        Funzione che inoltra i dati ricevuti dal client ai server
        Parameters
        ----------
        dato : dato da inoltrare ai server (nome del file o contenuto del file)

        Returns
        -------

        """
        try:
            # ottengo l'indirizzo e la porta del server a cui inoltrare la richiesta
            server_address, server_port = self.round_robin()
            # creo una socket per la connessione con il server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # mi connetto con il server
            server_socket.connect((server_address, server_port))
            # invio il dato al server
            server_socket.sendall(dato)
            self.ricevi_dai_server(server_socket)
            server_socket.close()
            time.sleep(0.2)
        except:
            print("C'è stato un errore")



    def round_robin(self):
        """
        Algoritmo di ROUND ROBIN che inoltra a turno una richiesta del client a ciascun server.
        Quando raggiunge la fine dell'elenco, il sistema di bilanciamento del carico torna indietro e scende nuovamente nell'elenco
        """
        while True:

            # Scegli il prossimo server nell'ordine circolare della lista
            server_address = self.SERVERS[self.CURRENT_SERVER_INDEX]
            server_port = self.PORTS[self.CURRENT_SERVER_PORT_INDEX]

            # Verifica se il server selezionato è attivo (flag True) e non sovraccarico (flag False)
            if self.SERVER_FLAGS[self.CURRENT_SERVER_INDEX] and not self.SERVER_SOVRACCARICO_FLAGS[self.CURRENT_SERVER_INDEX]:
                break  # Esci dal ciclo se il server è attivo e non sovraccarico

            # Se il server non è attivo, passa al successivo nell'ordine
            self.CURRENT_SERVER_INDEX = (self.CURRENT_SERVER_INDEX + 1) % len(self.SERVERS)
            self.CURRENT_SERVER_PORT_INDEX = (self.CURRENT_SERVER_PORT_INDEX + 1) % len(self.PORTS)

        # Passa al successivo nell'ordine per la prossima richiesta
        self.CURRENT_SERVER_INDEX = (self.CURRENT_SERVER_INDEX + 1) % len(self.SERVERS)
        self.CURRENT_SERVER_PORT_INDEX = (self.CURRENT_SERVER_PORT_INDEX + 1) % len(self.PORTS)

        return server_address, server_port  # Restituisci l'indirizzo del server attivo




    def monitoraggio_status_server(self):
        """
        Funzione che monitora lo stato dei server, in particolare controlla se sono attivi, spenti e se sono sovraccarichi
        Returns
        -------

        """
        while True:
            #self.accensione_server()
            # Per ogni server nella lista degli indirizzi dei server
            for i, server_address in enumerate(self.SERVERS):
                # Creo una connessione con il server per verificare il suo stato
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.settimeout(1)  # Timeout per la connessione
                try:
                    # provo a connettermi al server
                    server_socket.connect((server_address, self.PORTS[i]))
                    # ricevo la notifica che mi informa del carico del server
                    notifica = server_socket.recv(1024).decode('utf-8')
                    if notifica == "Sovraccarico":
                        self.SERVER_SOVRACCARICO_FLAGS[i] = True
                    # chiudo la socket del server
                    server_socket.close()
                    # Se la connessione riesce, il server è attivo, quindi aggiorno la flag in True
                    self.SERVER_FLAGS[i] = True
                except (socket.timeout, ConnectionRefusedError):
                    # Se la connessione fallisce, il server è inattivo, quindi aggiorno la flag in False
                    self.SERVER_FLAGS[i] = False
            time.sleep(1)


    def monitoraggio_sovraccarico_server(self, server_socket):
        pass



    def ricevi_dai_server(self, server_socket):
        """
        Funzione che riceve i dati dai server
        Parameters
        ----------
        server_socket

        Returns
        -------

        """
        try:
            risposta = server_socket.recv(1024).decode('utf-8')
            print(risposta)
        except:
            print("Errore nella ricezione della risposta dal server")
            sys.exit()


    # def accensione_server(self):
    #     """
    #     Funzione che accende i server, in particolare all'avvio del load balancer viene accesso il primo server e gli altri vengono accesi all'occorrenza
    #     Returns
    #     -------
    #
    #     """
    #     # lancio il primo server
    #     self.avvia_processo("server_ftp1.py")
    #     while True:
    #         # se il primo server è attivo e sovraccarico, allora accendo il secondo server
    #         if self.SERVER_FLAGS[0] and self.SERVER_SOVRACCARICO_FLAGS[0]:
    #             self.avvia_processo("server_ftp2.py")
    #         # se il secondo server è attivo e sovraccarico, allora accendo il terzo server
    #         if self.SERVER_FLAGS[1] and self.SERVER_SOVRACCARICO_FLAGS[1]:
    #             self.avvia_processo("server_ftp3.py")
    #         # se il terzo server è attivo e sovraccarico, allora accendo il primo server
    #         if self.SERVER_FLAGS[2] and self.SERVER_SOVRACCARICO_FLAGS[2]:
    #
    #
    #
    #
    #
    # def avvia_processo(self, script):
    #     return subprocess.Popen(["python", script])
    #
    # def termina_processo(self, processo):
    #     processo.terminate()