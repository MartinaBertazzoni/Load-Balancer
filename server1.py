import socket
import threading
import sys

class server(object):
    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = 5002
        self.clients = []
        self.active_clients = []
        self.richieste = {}  # la chiave è ip del client, argomento nome richieste
        self.comandi = {}



    def socket_server(self):
        """
        Funzione che crea la socket del server e crea un thread che rimane in ascolto per ricevere i comandi dal load balancer
        """
        # creo una socket server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # collego la socket al server
        server_socket.bind((self.ip, self.port))
        # metto in ascolto il server
        server_socket.listen()
        print(f"Server in ascolto su {self.ip}:{self.port}")
        # creo un thread che rimane in ascolto per ricevere i comandi dal load balancer
        thread_gestione_client = threading.Thread(target=self.gestione_client, args=(server_socket,))
        thread_gestione_client.start()
        thread_gestione_client.join()
        server_socket.close()


    def gestione_client(self, server_socket):
        """
        Funzione che rimane in ascolto per ricevere i comandi dal load balancer
        """
        while True:
            # accetto le connessioni in entrata
            client_socket, client_ip = server_socket.accept()
            # avvio un thread per gestire le richieste del client
            thread_richieste_client = threading.Thread(target=self.richieste_client, args=(client_socket,))
            thread_richieste_client.start()
            # se il client si disconnette, termina il thread
            if client_socket not in self.clients:
                thread_richieste_client.join()


    def richieste_client(self, client_socket):
        """
        Funzione che gestisce le richieste del client
        """
        while True:
            # ricevo i comandi dal load balancer
            data = client_socket.recv(1024)
            # se non ricevo più comandi, esco dal ciclo
            if not data:
                break
            # decodifico i comandi
            comando = data.decode("utf-8")
            # inserisco i comandi nella lista dei comandi da svolgere
            self.richieste[client_socket] = comando
            # richiamo il metodo per eseguire i comandi
            self.esegui_comandi(comando, client_socket)
        client_socket.close()


    def esegui_comandi(self, comando, client_socket):
        pass

    # MANCA L'ATTRIBUTO CHE INVIA LA SOLUZIONE DEI COMANDI AL CLIENT




