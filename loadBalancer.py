"""
Implementazione del load balancer
"""
import threading
import socket
import logging
from pynput import keyboard  # Import pynput library
import sys
import multiprocessing

# commento per testare il commit

# commento per testare il commit

class LoadBalancer(object):

    def __init__(self):
        """
        Costruttore della classe loadBalancer
        """

        
        # porta in cui si mette in ascolto il server
        self.port = 60002
        self.ip = '127.0.0.1'
        # lista che tiene  conto dei client collegati con il loadBalancer
        self.clients = []
        self.active_clients=[]
        """(da implementare) il loadbalancer memorizza le richieste dei client qualora,
        in caso di errore di trasmissione dei comandi al server, 
        quest'ultimo inivii la richiesta al loadbalancer di ricevere nuovamente i compiti"""
        self.richieste = {}  # la chiave è ip del client, argomento nome richieste
        self.servers = ["127.0.0.1", "127.0.0.1", "127.0.0.1"]
        self.port_server = [5007, 5008, 5009]
        self.current_server_index = 0
        self.current_server_port_index = 0
        self.server_flags = [False] * len(self.servers)

        # registro attività loadBalancer e creazione del file loadbalancer.log
        self.log_file = 'loadbalancer.log'
        logging.basicConfig(filename=self.log_file, level=logging.INFO, format='%(levelname)s - %(message)s')

        self.shutdown_event = multiprocessing.Event()  # Event to signal shutdown
        self.keyboard_listener = None  # Store the keyboard listener object
        self.keyboard_process = multiprocessing.Process(target=self.monitor_keyboard_input)

    def monitor_keyboard_input(self):
         # Create a keyboard listener with a timeout
        with keyboard.Listener(on_press=self.handle_esc_key) as self.keyboard_listener:
            while not self.shutdown_event.is_set():
                pass



    def handle_esc_key(self, key):
        if key == keyboard.Key.esc:
            self.shutdown_event.set()

    def shutdown(self):
        print("Shutting down...")
        if self.shutdown_event.is_set():
            if hasattr(self, 'balancer_socket') and self.balancer_socket:
                self.balancer_socket.close()
            if len(self.active_clients)!=0:
                for client_socket in self.active_clients:
                    client_socket.close()
            for thread in threading.enumerate():
                if not thread.daemon and thread != threading.main_thread():
        
                    thread.join()
            print("Load balancer has been shut down.")
            sys.exit(0)
            
    def avvio_loadbalancer(self):
        """
        funzione che aavvia i metodi del loadbalancer, nel caso apre e chiude thread per gestire comunicazioni con client
        e server
        """
        pass

    def gestione_comunicazione_client(self, client_socket):
        """
        Funzione che gestisce la comunicazione con il client:
        il server riceve i dati dal client e invia una risposta di avvenuta connessione;
        in seguito invierà il comando ad un server per elaborare la richiesta
        """
        # funzione che mette il log di connessione nel file loadbalancer.log al loadbalancer
        logging.info(f'Client connesso: {client_socket.getpeername()}')
        
        try:
            while True:
                # il loadBalancer riceve i dati dal client
                data = client_socket.recv(4096)
                message = data.decode("utf-8")
                if message.strip() == "exit":  # strips leva gli spazi bianchi
                    print(f'{client_socket.getpeername()} si sta disconnettendo dal loadbalancer')
                    # funzione che mette il log di disconnessione nel file loadbalancer.log al loadbalancer
                    logging.info(f'Disconnessione da {client_socket.getpeername()}')
                    exit_response = "Disconnessione avvenuta con successo"
                    client_socket.send(exit_response.encode())
                    # il loadbalancer elimina dalla lista dei clients attivi il client che si sta disconnettendo e chiude il collegamento
                    self.active_clients.remove(client_socket)
                    break
                else:
                    print("Messaggio ricevuto dal client: {}".format(message))
                    # funzione che mette il log di ricervuta richesta nel file loadbalancer.log al loadbalancer
                    logging.info(f'Richiesta ricevuta dal Client {client_socket.getpeername()}:{message}')

                    # DEVO CHIAMARE LA FUNZIONE CHE INOLTRA LA RICHIESTA AD UN SERVER CON MECCANISMO ROUND ROBIN
                    self.route_message(client_socket, data)
        except Exception as e:
            print("Errore durante la comunicazione con il client:", e)
            self.active_clients.remove(client_socket)
        finally:
            client_socket.close()

    def round_robin(self):
        """
        Algoritmo di ROUND ROBIN che inoltra a turno una richiesta del client a ciascun server.
        Quando raggiunge la fine dell'elenco, il sistema di bilanciamento del carico torna indietro e scende nuovamente nell'elenco

        """
        while True:
            # MONITORO LO STATO DEI SERVER PRIMA DI SCEGLIERE
            self.monitoraggio_server()
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


    def route_message(self, client_socket, data):
        try:
            server_address, server_port = self.round_robin()
            # funzione che mette il log di richiesta del Client inoltrata allo specifico Server nel file loadbalancer.log al loadbalancer
            logging.info(
                f'Inoltro richiesta del Client {client_socket.getpeername()} al server {server_address}:{server_port}')

            # si crea la connessione con il server, la richiesta viene inviata e, quando è stata ricevuta, la connessione viene chiusa
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((server_address, server_port))
            server_socket.sendall(data)
            response = server_socket.recv(1024)
            server_socket.close()
            client_socket.send(response)
        except:
            print("C'è stato un errore")

    def creazione_socket_loadBalancer(self):

        """
        Funzione che crea la socket TCP del loadBalancer per connetterlo all'host ed ai server

        (da modificare)

        Returns
        -------
        None.
        """

        # Creazione della socket del server
        self.balancer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Binding della socket all'host e alla porta
        self.balancer_socket.bind((self.ip, self.port))
        self.balancer_socket.listen()
        print("Server di load balancing in ascolto su {}:{}".format(self.ip, self.port))
        connessione=threading.Thread(target=self.connessione_client)
        thread=threading.Thread(target=self.thread_client)
        connessione.start()
        thread.start()
    
        

    def connessione_client(self):
                
        """
        Funzione che accetta le connessioni in entrata e le gestisce

        """

        while not self.shutdown_event.is_set():
            try:
                self.balancer_socket.settimeout(1)
                try:
                    # Accetta le connessioni in entrata
                    client_socket, client_ip = self.balancer_socket.accept()
                    # Aggiunge il client alla lista dei client connessi
                    self.clients.append(client_socket)
                    # Commento di riuscita connessione con il client
                    print("Connessione accettata da {}:{}".format(client_ip[0], client_ip[1]))
                except socket.timeout:
                    continue
            except:    
                continue
            
    def thread_client(self):
        active_threads = []  # List to store active client threads

        while not self.shutdown_event.is_set():
            if len(self.clients) != 0:
                client_socket = self.clients[0]
                print(self.clients)
                self.clients.remove(client_socket)
                self.active_clients.append(client_socket)

                # Avvia un thread separato per gestire il client: per ogni client viene aperto un thread separato
                client_thread = threading.Thread(target=self.gestione_comunicazione_client, args=(client_socket,))
                client_thread.start()
                active_threads.append(client_thread)
            else:
                    # Check for and remove completed threads
                for thread in active_threads:
                    if not thread.is_alive():
                    
                        active_threads.remove(thread)
                        thread.join() 
                        print('thread client chiuso')
                continue

            


    def monitoraggio_server(self):
        """
        metodo o insieme di metodi che ricevono e salvano le informazioni dello status (numero di richieste,
        operativo o non operativo, carico computazionale solo se troviamo funzioni che ci consentono di osservarlo) di ogni sever
        in tempi regolari
        """
        for i, server_address in enumerate(self.servers):
            # Qui creo una connessione con il server per verificare il suo stato
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.settimeout(2)  # Timeout per la connessione
            try:
                server_socket.connect((server_address, self.port_server[i]))
                server_socket.close()
                # Se la connessione riesce, il server è attivo, quindi aggiorno la flag in True
                self.server_flags[i] = True
            except (socket.timeout, ConnectionRefusedError):
                # Se la connessione fallisce, il server è inattivo, quindi aggiorno la flag in False
                self.server_flags[i] = False

        # Attendi un certo intervallo di tempo prima di effettuare un nuovo controllo
        #time.sleep(5)  # Controlla lo stato dei server ogni 5 secondi
        print(self.server_flags)

    def gestione_comunicazione_server(self):
        """
        funzione che invia e distribuisce le richieste(tramite la funzione di algortimo nel nostro caso il round robin).
        manda il segnale di chiusura della richiesta, reinvia il risulatato della richiesta

        """
        pass




if __name__ == '__main__':
    load_balancer = LoadBalancer()
    load_balancer.creazione_socket_loadBalancer()
    

    load_balancer.keyboard_process.start()

    while True:
        if load_balancer.shutdown_event.is_set():
            load_balancer.shutdown()
            break
    

    
