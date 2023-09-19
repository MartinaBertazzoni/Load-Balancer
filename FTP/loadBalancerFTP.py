import sys
import socket
import threading
import json
import time
import logging
from pynput import keyboard  # Import pynput library
import multiprocessing
import threading

class LoadBalancer(object):
    def __init__(self):
        self.balancer_socket = None
        self.port = 60003  # porta in cui si mette in ascolto il server
        self.ip = '127.0.0.1'
        self.clients=[]
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
            if len(self.active_clients) != 0:
                for client_socket in self.active_clients:
                    client_socket.close()
            for thread in threading.enumerate():
                if not thread.daemon and thread != threading.main_thread():
                    thread.join()
            print("Load balancer has been shut down.")
            sys.exit(0)

    def creo_socket_loadBalancer(self):
        self.balancer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Binding della socket all'host e alla porta
        self.balancer_socket.bind((self.ip, self.port))
        self.balancer_socket.listen()
        print("Server di load balancing in ascolto su {}:{}".format(self.ip, self.port))

    def connetto_il_client(self):
        while True:
            try:
                # Accetta le connessioni in entrata
                client_socket, client_ip = self.balancer_socket.accept()
                # Aggiunge il client alla lista dei client connessi
                self.clients.append(self.balancer_socket)
                # Commento di riuscita connessione con il client
                print("Connessione accettata da {}:{}".format(client_ip[0], client_ip[1]))
                ricezione_dati = threading.Thread(target=self.ricevo_file_dal_client, args=(client_socket,))
                ricezione_dati.start()
                ricezione_dati.join()
            except Exception as e:
                print("Errore durante la comunicazione con il client:", e)


    def ricevo_file_dal_client(self, client_socket):
        try:
            while True:
                # riceve il nome del file
                self.filepath=client_socket.recv(4096).decode("utf-8")
                print("il path", self.filepath)
                if not self.filepath:
                    break
                json_data_encoded = client_socket.recv(4096).decode("utf-8")
                if not json_data_encoded:
                    break
                # Decodifica il file JSON
                json_data = json.loads(json_data_encoded)
                # Estrai il titolo e il contenuto dal file JSON
                titolo = json_data.get("titolo", "")
                contenuto = json_data.get("contenuto", "")
                print(f"Titolo ricevuto dal client: {titolo}")
                print(f"Contenuto ricevuto dal client: {contenuto}")
                # creo un thread che invia i file ai server
                invia_file_ai_server = threading.Thread(target=self.invia_ai_server, args=(client_socket,))
                invia_file_ai_server.start()
                invia_file_ai_server.join()
        except Exception as e:
            print("Errore durante la comunicazione con il client:", e)
        finally:
            client_socket.close()


    def invia_ai_server(self,client_socket):
        try:
            server_address, server_port = self.round_robin()
            print(server_address, server_port)
            # funzione che mette il log di richiesta del Client inoltrata allo specifico Server nel file loadbalancer.log al loadbalancer
            logging.info(
                f'Inoltro richiesta del Client {client_socket.getpeername()} al server {server_address}:{server_port}')
            # creo una socket per la connessione con il server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # mi connetto con il server
            server_socket.connect((server_address, server_port))

            #DA IMPLEMENTARE
            with open(self.filepath, 'r', encoding='utf-8') as file:
                json_data = file.read()
            server_socket.send(json_data.encode("utf-8"))

            # ricevo risposte dai server
            #risposta_dal_server = threading.Thread(target=self.ricevi_risposta_server, args=(server_socket,client_socket))
            #risposta_dal_server.start()
            #risposta_dal_server.join()
        except socket.error as error:
            print(f"Errore di comunicazione con il server: {error}")
            sys.exit(1)

    def monitoraggio_server(self):
        """
        metodo o insieme di metodi che ricevono e salvano le informazioni dello status (numero di richieste,
        operativo o non operativo, carico computazionale solo se troviamo funzioni che ci consentono di osservarlo) di ogni sever
        in tempi regolari
        """
        while not self.shutdown_event.is_set():
            for i, server_address in enumerate(self.servers):
                # Qui creo una connessione con il server per verificare il suo stato
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.settimeout(1)  # Timeout per la connessione
                try:
                    server_socket.connect((server_address, self.port_server[i]))
                    server_socket.close()
                    # Se la connessione riesce, il server è attivo, quindi aggiorno la flag in True
                    self.server_flags[i] = True
                    print("True")
                except (socket.timeout, ConnectionRefusedError):
                    # Se la connessione fallisce, il server è inattivo, quindi aggiorno la flag in False
                    self.server_flags[i] = False
                    print("False")


    def round_robin(self):
        """
        Algoritmo di ROUND ROBIN che inoltra a turno una richiesta del client a ciascun server.
        Quando raggiunge la fine dell'elenco, il sistema di bilanciamento del carico torna indietro e scende nuovamente nell'elenco
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

    def ricevi_risposta_server(self,server_socket, client_socket):
        try:
            message_from_server = server_socket.recv(1024).decode("utf-8")
            print(message_from_server)
            # rispondo al client
            client_socket.send(message_from_server.encode("utf-8"))
        except socket.error as error:
            print(f"Impossibile ricevere dati dal server: {error}")
            sys.exit(1)






    def weighted_round_robin(self):
        pass
    def invia_dati_al_server(self):
        pass

    def invia_risposta_al_client(self):
        pass

    def monitoraggio_status_server(self):
        pass

    def monitoraggio_carico_server(self):
        pass

    def monitoraggio_client_connessi(self):
        pass





if __name__ == "__main__":
    load = LoadBalancer()
    monitoraggio = threading.Thread(target=load.monitoraggio_server)
    monitoraggio.start()
    load.creo_socket_loadBalancer()
    load.connetto_il_client()
