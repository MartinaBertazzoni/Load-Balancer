"""
Implementazione del load balancer
"""
import threading
import socket
import logging
from pynput import keyboard  # Import pynput library
import sys
import multiprocessing

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
        Metodo che gestisce la comunicazione del loadBalancer con il client:
            il loadBalancer riceve i dati dal client e invia una risposta di avvenuta connessione;
            in seguito invia il comando ad un server per elaborare la richiesta

        Parameters
        ----------
        client_socket: socket
        
        Returns
        -------
        None.
        
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
        Metodo che implementa l'algoritmo di Round Robin. L'algoritmo inoltra a turno una richiesta del client a ciascun server
        in maniera sequenziale. Quando viene inoltrata la richiesta all'ultimo server della lista, il sistema di bilanciamento 
        del carico ricomincia a scorrere la lista a partire dal primo server.

        Returns
        -------
        server_address: str
            ip del server attivo
        server_port: int
            porta del server attivo

        """
        while True:
            # Richiamo il metodo di monitoraggio del server, che riporta quali sono i server attivi e quelli inattivi
            self.monitoraggio_server()
            # Scelgo il prossimo server
            server_address = self.servers[self.current_server_index]
            server_port = self.port_server[self.current_server_port_index]

            # Verifico se il server selezionato è attivo (flag True); se sì, esci dal ciclo
            if self.server_flags[self.current_server_index]:
                break

            # Se il server non è attivo, passa al server successivo
            self.current_server_index = (self.current_server_index + 1) % len(self.servers)
            self.current_server_port_index = (self.current_server_port_index + 1) % len(self.port_server)

        # Passa al successivo nell'ordine per la prossima richiesta
        self.current_server_index = (self.current_server_index + 1) % len(self.servers)
        self.current_server_port_index = (self.current_server_port_index + 1) % len(self.port_server)

        return server_address, server_port  # Restituisci l'indirizzo del server attivo


    def route_message(self, client_socket, data):
        
        """
        Metodo che connette il loadBalancer al server appena selezionato con l'algoritmo di Round Robin, gli inoltra
        la richiesta, riceve la risposta e la inoltra al client.
        
        Parameters
        ----------
        client_socket: socket
        
        data: 

        Returns
        -------
        None.

        """
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
        Metodo che crea la socket TCP del loadBalancer 

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
        Metodo che connette il loadBalancer con il client
        
        Returns
        -------
        None.

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
        """
        

        Returns
        -------
        None.

        """
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
        Metodo che verifica lo stato di attività o inattività dei server. 

        Returns
        -------
        server_flags: list[bool]
            lista di valori booleani che indicano l'attività (True) 
            o l'inattività (False) di ogni server collegato al loadBalancer
        
        """
        for i, server_address in enumerate(self.servers):
            # Creo una connessione con il server per verificare il suo stato
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
        print(self.server_flags)



if __name__ == '__main__':
    load_balancer = LoadBalancer()
    load_balancer.creazione_socket_loadBalancer()
    

    load_balancer.keyboard_process.start()

    while True:
        if load_balancer.shutdown_event.is_set():
            load_balancer.shutdown()
            break
    

    
