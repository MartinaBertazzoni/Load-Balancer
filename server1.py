import socket
import threading
import random

class server(object):
    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = 5007
        self.clients = []
        self.active_clients = []
        self.richieste = {}  # la chiave è ip del client, argomento nome richieste
       

    def socket_server(self):
        
        """
        
        Metodo che crea la socket del server e crea un thread che rimane in ascolto per ricevere i comandi dal loadBalancer

        Returns
        -------
        None.

        """
        # creo una socket server e la metto in ascolto
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.port))
        server_socket.listen()
        print(f"Server in ascolto su {self.ip}:{self.port}")
        # creo un thread che rimane in ascolto per ricevere i comandi dal load balancer
        thread_gestione_client = threading.Thread(target=self.gestione_client, args=(server_socket,))
        thread_gestione_client.start()
        thread_gestione_client.join()
        server_socket.close()


    def gestione_client(self, server_socket):
        
        """
        Metodo che rimane in ascolto per ricevere i comandi dal loadBalancer

        Parameters
        ----------
        server_socket : socket

        Returns
        -------
        None.

        """
        while True:
            # accetto le connessioni in entrata
            client_socket, client_ip = server_socket.accept()
            # avvio un thread per gestire le richieste del client
            thread_richieste_client = threading.Thread(target=self.richieste_client, args=(client_socket,client_ip,))
            thread_richieste_client.start()
            # se il client si disconnette, termina il thread
            if client_socket not in self.clients:
                thread_richieste_client.join()
        


    def richieste_client(self, client_socket, client_ip):
        """

        Parameters
        ----------
        client_socket : socket
        client_ip : str

        Returns
        -------
        None.

        """
        
        while True:
            # ricevo i comandi dal load balancer; se non ricevo più comandi, esco dal ciclo
            data = client_socket.recv(1024)
            if not data:
                break
            print('{}: received message: {}'.format(client_ip, data.decode('utf-8')))
            comando = data.decode("utf-8")  # decodifico i comandi
            self.richieste[client_socket] = comando  # inserisco i comandi nella lista dei comandi da svolgere
            risultato = self.esegui_comandi(comando, client_socket)  # chiamo il metodo per eseguire i comandi ricevuti
            print(risultato)
            risultato_stringa=str(risultato)
            client_socket.sendall(risultato_stringa.encode('utf-8')) #invio i risultati al loadBalancer
        client_socket.close()


    def esegui_comandi(self, comando, client_socket):
        """
        

        Parameters
        ----------
        comando : str
             stringa che contiene il comando da eseguire
        client_socket : socket

        Returns
        -------
        soluzione : dict
             dizionario che contiene i numeri scelti, l'operazione da svolgere e il risultato

        """
        # creo due valori random A e B che servono per i calcoli
        A = random.randint(1, 50)
        B = random.randint(1, 50)
        if comando == "somma":
            risultato=A+B
        if comando == "sottrazione":
            risultato=A-B
        if comando == "moltiplicazione":
            risultato=A*B
        if comando == "divisione":
            risultato=A/B
        soluzione={'A':A,
                   'B':B,
                   'operazione': comando,
                   'risultato': risultato}
        return soluzione
        

    # MANCA L'ATTRIBUTO CHE INVIA LA SOLUZIONE DEI COMANDI AL CLIENT



if __name__ == "__main__":
    server = server()
    server.socket_server()


