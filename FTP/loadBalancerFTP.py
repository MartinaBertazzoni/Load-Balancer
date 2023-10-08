import sys
import socket
import logging
import threading
import json
from queue import Queue
import time

class LoadBalancer(object):
    def __init__(self):
        """
        Costruttore della classe LoadBalancer
        """
        self.balancer_socket = None
        self.port = 60002 # porta in cui si mette in ascolto il server
        self.ip = '127.0.0.1'
        self.nomi_file_ricevuti = []
        self.file_ricevuti = []
        self.filepath = None
        self.servers = ["127.0.0.1", "127.0.0.1", "127.0.0.1"]
        self.port_server = [5001, 5002, 5003]
        self.current_server_index = 0
        self.request_queue = Queue()  # Coda delle richieste in arrivo
        self.server_flags_connection = [False] * len(self.servers)
        self.server_sovracarichi=[False] * len(self.servers)
        self.numero_della_richiesta=0
        self.monitoraggio_stato_server = threading.Thread(target=self.monitoraggio_stato_server)
        self.monitoraggio_stato_server.daemon = True
        self.monitoraggio_stato_server.start()
        # registro attività loadBalancer e creazione del file loadbalancer.log
        self.log_file = 'loadbalancer.log'
        logging.basicConfig(filename=self.log_file, level=logging.INFO, format='%(levelname)s - %(message)s', filemode='w')


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
        message_0 = "Server di load balancing in ascolto su {}:{}".format(self.ip, self.port)   
        print(message_0)
        # Registra il messaggio nel file di log
        logging.info(message_0)  


    def connetto_il_client(self):
        """
        Metodo che connette il load balancer con il client, crea un thread per ricevere i file dal client
        e un thread per gestire la coda delle richieste in arrivo dal client

        :return: None
        """
        try:
            client_socket, client_ip = self.balancer_socket.accept() # Accetta le connessioni in entrata
            message_1 = "Connessione accettata da {}:{}".format(client_ip[0], client_ip[1])
            print(message_1)
            # Registra il messaggio nel file di log
            logging.info(message_1) 
            # attivo ricezione file dal client
            ricezione_file = threading.Thread(target=self.ricevo_file_dal_client, args=(client_socket,))
            ricezione_file.start()
            # il load balancer invia i file contenuti nella coda ai server
            invio_file_ai_server = threading.Thread(target=self.gestisci_coda_richieste)
            invio_file_ai_server.start()
        except Exception as e:
            error_message_0 = "Errore durante la comunicazione con il client: {}".format(e)
            print(error_message_0)
            # Registra il messaggio di errore nel file di log
            logging.exception(error_message_0)  


    def ricevo_file_dal_client(self, client_socket):
        """
        Metodo che riceve il file JSON dal client e inserisce il contenuto del file all'interno della
        coda delle richieste

        :param client_socket: socket del client
        :return: None
        """
        try:
            while True:
                file_ricevuto = client_socket.recv(4096).decode("utf-8")
                file = json.loads(file_ricevuto) # converto il file in un dizionario
                titolo = file.get("titolo", "")
                self.nomi_file_ricevuti.append(titolo)
                message_2 = "Il loadBalancer ha ricevuto dal client il file: {}".format(titolo) 
                print(message_2)
                # Registra il messaggio nel file di log
                logging.info(message_2)
                self.request_queue.put((client_socket, file, titolo)) # inserisco la richiesta nella coda
        except Exception as e:
            error_message_1 = "Errore durante la comunicazione con il client: {}".format(e)
            print(error_message_1)
            # Registra il messaggio di errore nel file di log
            logging.exception(error_message_1)  


    def gestisci_coda_richieste(self):
        """
        Metodo che estrae il primo elemento dalla coda delle richieste e lo invia al server

        :return: None
        """
        while True:
            client_socket, file, titolo = self.request_queue.get()  # estraggo il primo elemento dalla coda
            time.sleep(0.2)
            self.invia_ai_server(client_socket, file, titolo)


    def invia_ai_server(self, client_socket, file , titolo):
        """
        Metodo che invia il file JSON al server scelto dall'algoritmo Round Robin

        :param client_socket:
        :return:
        """
        try:
            server_address, server_port = self.round_robin()
            message_3 = "Server scelto: {}".format(server_port)
            print(message_3)
            # Registra il messaggio nel file di log
            logging.info(message_3)
            # Aggiorno il file di log loadbalancer.log
            message_4 = f'Inoltro richiesta del Client {client_socket.getpeername()} al Server {server_address}:{server_port}'
            logging.info(message_4)
            self.invia_al_server_scelto(server_address, server_port, file, titolo)  # invio il file al server scelto dal round robin
        except socket.error as error:
            error_message_2 = "Errore durante la comunicazione con il server: {}".format(error)
            print(error_message_2)
            # Registra il messaggio di errore nel file di log
            logging.exception(error_message_2)  
            sys.exit(1)

    def invia_al_server_scelto(self, server_address, server_port, file, titolo):
        """
        Metodo che connette il load balancer con il server scelto e gli invia il contenuto del file

        :param server_address: ip del server scelto
        :param server_port: porta del server scelto
        :param file: file da inviare
        :param titolo: titolo del file da inviare
        :return: None

        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # connetto il load balancer al server scelto
        server_socket.connect((server_address, server_port))
        self.numero_della_richiesta += 1
        message_5 = "Numero della richiesta elaborata: {}".format(self.numero_della_richiesta)
        print(message_5)
        # Registra il messaggio nel file di log
        logging.info(message_5)
        file['numero_richiesta'] = self.numero_della_richiesta
        message_6 = f"Ho inviato il file {titolo} al server {server_port}, status:{self.server_sovracarichi[self.port_server.index(server_port)]} "
        print(message_6)
        # Registra il messaggio nel file di log
        logging.info(message_6)
        file_da_inviare = json.dumps(file)
        server_socket.send(file_da_inviare.encode("utf-8"))
        server_socket.close()

    def monitoraggio_stato_server(self):
        """
        Metodo che monitora lo stato di connessione dei server provandoli a mettere in connessione con il load balancer.
        In caso di esito positivo, la flag del server diventa True, altrimenti è False. Inoltre, svolge un controllo
        sullo stato del carico dei server.

        :return: None
        """
        while True:
            for i, server_address in enumerate(self.servers):
                # creo una connessione con il server per verificare il suo stato di connessione
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.settimeout(1)  # Timeout per la connessione
                try:
                    server_socket.connect((server_address, self.port_server[i]))
                    self.monitoraggio_carico_server(i, server_socket)  # monitoro il carico del server
                    # Se la connessione riesce, il server è attivo, quindi aggiorno la flag in True
                    self.server_flags_connection[i] = True
                except (socket.timeout, ConnectionRefusedError):
                    # Se la connessione fallisce, il server è inattivo, quindi aggiorno la flag in False
                    self.server_flags_connection[i] = False

    def monitoraggio_carico_server(self, i, server_socket):
        """
        Metodo che monitora il carico del server; in particolare, in seguito a una richiesta
        del load balancer, riceve dal server una flag, dove True ne indica
        lo stato di sovraccarico, mentre False il contrario, e quindi il permesso di inviargli file

        :param i: indice del server scelto
        :param server_socket: socket del server
        :return: None

        """
        # creo il messaggio di richiesta di monitoraggio
        messaggio_di_monitoraggio = {'request_type': 'richiesta_status'}
        # lo trasformo in una stringa e lo invio
        richiesta_status = json.dumps(messaggio_di_monitoraggio)
        server_socket.send(richiesta_status.encode())
        # ricevo la risposta boolena: sovraccarico = True, non in sovraccarico = False
        status = server_socket.recv(1)
        # lo converto da byte a valore booleano
        status = bool(int.from_bytes(status, byteorder='big'))
        self.server_sovracarichi[i] = status
        server_socket.close()


    def round_robin(self):
        """
        Metodo che implementa l'algoritmo di bilanciamento del carico Round Robin, il quale inoltra una richiesta
        ad ogni server in maniera sequenziale.

        :return:
        server_address: ip del server
        server_port: porta del server

        """
        while True:
            # Scegli il prossimo server nell'ordine circolare
            server_address = self.servers[self.current_server_index]
            server_port = self.port_server[self.current_server_index]
            # Verifica che il server selezionato è attivo (flag True) e non sovraccarico (flag False); in caso contrario, cambia server
            if self.server_flags_connection[self.current_server_index] and self.server_sovracarichi[self.current_server_index]==False:
                break
            # Se il server non è attivo, passa al successivo nell'ordine
            self.current_server_index = (self.current_server_index + 1) % len(self.servers)
        # Passa al successivo nell'ordine per la prossima richiesta
        self.current_server_index = (self.current_server_index + 1) % len(self.servers)
        return server_address, server_port  # Restituisci l'indirizzo del server attivo


if __name__ == "__main__":
    load = LoadBalancer()
    load.avvio_loadbalancer()




