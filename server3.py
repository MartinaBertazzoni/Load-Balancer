import socket
import threading
import random
import multiprocessing
from pynput import keyboard
import sys

# commento per provare il commit

class server(object):
    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = 5009
        self.clients = []
        self.active_clients = []
        self.richieste = {}  # la chiave è ip del client, argomento nome richieste
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
                self.server_socket.close()
            if len(self.clients)!=0:
                for client_socket in self.active_clients:
                    client_socket.close()
            for thread in threading.enumerate():
                if not thread.daemon and thread != threading.main_thread():
                    thread.join()
            print("Load balancer has been shut down.")
            sys.exit(0)
                   

    def socket_server(self):
        """
        Funzione che crea la socket del server e crea un thread che rimane in ascolto per ricevere i comandi dal load balancer
        """
        # creo una socket server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # collego la socket al server
        self.server_socket.bind((self.ip, self.port))
        # metto in ascolto il server
        self.server_socket.listen()
        print(f"Server in ascolto su {self.ip}:{self.port}")
        # creo un thread che rimane in ascolto per ricevere i comandi dal load balancer
        thread_gestione_client = threading.Thread(target=self.gestione_client)
        thread_gestione_client.start()
        


    def gestione_client(self):
        """
        Funzione che rimane in ascolto per ricevere i comandi dal load balancer
        """
        while not self.shutdown_event :
            # accetto le connessioni in entrata
            client_socket, client_ip = self.server_socket.accept()
            # avvio un thread per gestire le richieste del client
            thread_richieste_client = threading.Thread(target=self.richieste_client, args=(client_socket,client_ip,))
            thread_richieste_client.start()
            # se il client si disconnette, termina il thread
            if client_socket not in self.clients:
                thread_richieste_client.join()
        


    def richieste_client(self, client_socket, client_ip):
        """
        Funzione che gestisce le richieste del client
        """
        while True:
            # ricevo i comandi dal load balancer
            data = client_socket.recv(1024)
            # se non ricevo più comandi, esco dal ciclo
            if not data:
                break
            print('{}: received message: {}'.format(client_ip, data.decode('utf-8')))
            # response = "Risposta dal server di destinazione"
            # client_socket.sendall(response.encode('utf-8'))
            # decodifico i comandi
            comando = data.decode("utf-8")
            # inserisco i comandi nella lista dei comandi da svolgere
            self.richieste[client_socket] = comando
            # richiamo il metodo per eseguire i comandi
            risultato = self.esegui_comandi(comando, client_socket)
            print(risultato)
            risultato_stringa=str(risultato)
            client_socket.sendall(risultato_stringa.encode('utf-8'))
        client_socket.close()


    def esegui_comandi(self, comando, client_socket):
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
        soluzione= f"Il risultato dell'operazione {comando} fra {A} e {B} è {risultato}"
        return soluzione

    # MANCA L'ATTRIBUTO CHE INVIA LA SOLUZIONE DEI COMANDI AL CLIENT



if __name__ == "__main__":
    server_instance = server()
    server_instance.socket_server()
    server_instance.keyboard_process.start()

    while True:
        if server_instance.shutdown_event.is_set():
            server_instance.shutdown()
            break