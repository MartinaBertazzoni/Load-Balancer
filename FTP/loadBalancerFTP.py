import sys
import socket
import logging
import threading
import json

class LoadBalancer(object):
    def __init__(self):
        self.balancer_socket = None
        self.port = 60002 # porta in cui si mette in ascolto il server
        self.ip = '127.0.0.1'
        self.clients = []
        self.nomi_file_ricevuti = []
        self.file_ricevuti = []
        self.filepath = None
        self.servers = ["127.0.0.1", "127.0.0.1", "127.0.0.1"]
        self.port_server = [5001, 5002, 5003]
        self.current_server_index = 0
        self.current_server_port_index = 0
        self.server_flags = [False] * len(self.servers)

        self.monitoraggio_stato_server = threading.Thread(target=self.monitoraggio_server)
        self.monitoraggio_stato_server.daemon = True
        self.monitoraggio_stato_server.start()

        # registro attività loadBalancer e creazione del file loadbalancer.log
        self.log_file = 'loadbalancer.log'
        logging.basicConfig(filename=self.log_file, level=logging.INFO, format='%(levelname)s - %(message)s')


    def avvio_loadbalancer(self):
        """
        Metodo che avvia il loadbalancer
        :return: None

        """
        self.creo_socket_loadBalancer()
        self.connetto_il_client()


    def creo_socket_loadBalancer(self):
        """
        Metodo che crea la socket del load balancer, e la mette in ascolto
        :return: None
        """
        self.balancer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Binding della socket all'host e alla porta
        self.balancer_socket.bind((self.ip, self.port))
        self.balancer_socket.listen()
        print("Server di load balancing in ascolto su {}:{}".format(self.ip, self.port))


    def connetto_il_client(self):
        """
        Metodo che connette il load balancer con il client, e crea un thread per ricevere i file dal client

        :return: None
        """
        try:
            while True:
                # Accetta le connessioni in entrata
                client_socket, client_ip = self.balancer_socket.accept()
                # Aggiunge il client alla lista dei client connessi
                self.clients.append(self.balancer_socket)
                # Commento di riuscita connessione con il client
                print("Connessione accettata da {}:{}".format(client_ip[0], client_ip[1]))

                ricezione_file = threading.Thread(target=self.ricevo_file_dal_client, args=(client_socket,))
                ricezione_file.start()
                ricezione_file.join()

        except Exception as e:
            print("Errore durante la comunicazione con il client:", e)



    def ricevo_file_dal_client(self, client_socket):
        """
        Metodo che riceve il file JSON dal client, lo divide in "titolo" e "contenuto" del file, e crea
        un thread per inviare il file ai server

        :param client_socket: socket del client
        :return: None
        """
        try:
            while True:
                # ricevo il file
                filepath = client_socket.recv(4096).decode("utf-8")
                if not filepath:
                    break
                self.nomi_file_ricevuti.append(filepath)
                print("Ho ricevuto il file", filepath)

                self.invia_ai_server(client_socket,filepath)

        except Exception as e:
            print("Errore durante la comunicazione con il client:", e)



    def invia_ai_server(self, client_socket,filepath):
        """
        Metodo che invia il file JSON al server scelto; dopo aver ottenuto l'ip e la porta del server considerato
        tramite il metodo Round Robin, il load balancer viene connesso al server in questione e gli invia
        il contenuto del file. In seguito, viene avviato un thread per gestire la risposta.

        :param client_socket:
        :return:
        """
        try:
            server_address, server_port = self.round_robin()
            print("server scelto", server_port)
            # funzione che mette il log di richiesta del Client inoltrata allo specifico Server nel file loadbalancer.log
            logging.info(
                f'Inoltro richiesta del Client {client_socket.getpeername()} al server {server_address}:{server_port}')

            # connetto il load balancer al server scelto
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((server_address, server_port))

            with open(filepath, 'r', encoding='utf-8') as file:
                contenuto = file.read()
            print("Ho inviato il file al server: ", filepath)
            server_socket.send(contenuto.encode("utf-8"))

            # ricevo risposta dal server
            self.ricevi_risposta_server(server_socket, client_socket)
        except socket.error as error:
            print(f"Errore di comunicazione con il server: {error}")
            sys.exit(1)

    def monitoraggio_server(self):
        """
        Metodo che monitora lo stato di connessione dei server provandoli a mettere in connessione con il load balancer.
        In caso di esito positivo, la flag del server diventa True, altrimenti è False.

        :return: None
        """

        while True:
            for i, server_address in enumerate(self.servers):
                # creo una connessione con il server per verificare il suo stato di connessione
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.settimeout(1)  # Timeout per la connessione
                try:
                    server_socket.connect((server_address, self.port_server[i]))
                    server_socket.close()
                    # Se la connessione riesce, il server è attivo, quindi aggiorno la flag in True
                    self.server_flags[i] = True
                except (socket.timeout, ConnectionRefusedError):
                    # Se la connessione fallisce, il server è inattivo, quindi aggiorno la flag in False
                    self.server_flags[i] = False


    def round_robin(self):
        """
        Metodo che implementa l'algoritmo di bilanciamento del carico Round Robin, che inoltra una richiesta
        ad ogni server in maniera sequenziale.

        :return:
        server_address: ip del server
        server_port: porta del server

        """
        while True:
            # Scegli il prossimo server nell'ordine circolare
            server_address = self.servers[self.current_server_index]
            server_port = self.port_server[self.current_server_port_index]

            # Verifica se il server selezionato è attivo (flag True)
            if self.server_flags[self.current_server_index]:
                break  # Esci dal ciclo se il server è attivo

            # Se il server non è attivo, passa al successivo nell'ordine
            self.current_server_index = (self.current_server_index + 1) % len(self.servers)
            self.current_server_port_index = (self.current_server_port_index + 1) % len(self.port_server)

        # Passa al successivo nell'ordine per la prossima richiesta
        self.current_server_index = (self.current_server_index + 1) % len(self.servers)
        self.current_server_port_index = (self.current_server_port_index + 1) % len(self.port_server)

        return server_address, server_port  # Restituisci l'indirizzo del server attivo


    def ricevi_risposta_server(self, server_socket, client_socket):
        """
        Metodo che riceve le risposte di avvenuta ricezione del server

        :param server_socket: socket del server
        :param client_socket: socket del client
        :return: None
        """
        try:
            message_from_server = server_socket.recv(1024).decode("utf-8")
            print(message_from_server)
            # rispondo al client
            client_socket.send(message_from_server.encode("utf-8"))
        except socket.error as error:
            print(f"Impossibile ricevere dati dal server: {error}")
            sys.exit(1)


    def monitoraggio_carico_server(self):
        pass

    def monitoraggio_client_connessi(self):
        pass


if __name__ == "__main__":
    load = LoadBalancer()
    load.avvio_loadbalancer()




