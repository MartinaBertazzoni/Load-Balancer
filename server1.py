import resource
import socket
import threading
import time
import psutil
import random


# commento per provare il commit

class server(object):
    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = 5007
        # tupla per la creazione della socket per il monitoraggio del server
        self.ADDRESS_MONITORAGGIO = ("127.0.0.1", 60006)
        self.clients = []
        self.active_clients = []
        self.richieste = {}  # la chiave è ip del client, argomento nome richieste
        self.LIMITE_CPU = 80*1024*1024 # 80 MB
        self.SOVRACCARICO = None




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
        thread_gestione_client = threading.Thread(target=self.accettazione_lb_per_richieste, args=(server_socket,))
        thread_gestione_client.start()
        thread_gestione_client.join()
        server_socket.close()

    def accettazione_lb_per_richieste(self, server_socket):
        """
        Funzione che rimane in ascolto per ricevere le richieste dal load balancer
        """
        while True:
            # accetto le connessioni in entrata
            lb_socket, lb_ip = server_socket.accept()
            # avvio un thread per gestire le richieste del client
            thread_richieste_client = threading.Thread(target=self.richieste_da_lb, args=(lb_socket, lb_ip,))
            thread_richieste_client.start()
            # se il client si disconnette, termina il thread
            if lb_socket not in self.clients:
                thread_richieste_client.join()

    def richieste_da_lb(self, lb_socket, lb_ip):
        """
        Funzione che gestisce le richieste del client
        """
        while True:
            # ricevo i comandi dal load balancer
            data = lb_socket.recv(1024)
            # se non ricevo più comandi, esco dal ciclo
            if not data:
                break
            print('{}: received message: {}'.format(lb_ip, data.decode('utf-8')))
            # response = "Risposta dal server di destinazione"
            # client_socket.sendall(response.encode('utf-8'))
            # decodifico i comandi
            comando = data.decode("utf-8")
            # inserisco i comandi nella lista dei comandi da svolgere
            self.richieste[lb_socket] = comando
            # richiamo il metodo per eseguire i comandi
            risultato = self.esegui_comandi(comando, lb_socket)
            print(risultato)
            risultato_stringa = str(risultato)
            lb_socket.sendall(risultato_stringa.encode('utf-8'))
        lb_socket.close()


    def socket_server_per_il_monitoraggio(self):
        """
        Funzione che crea la scoket per garantire il monitoraggio con il loadBalancer e invia la percentuale di cpu al load balancer
        Returns
        -------

        """
        # creo la socket per il monitoraggio
        socket_server_monitoraggio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # faccio il binding della socket
        socket_server_monitoraggio.bind(self.ADDRESS_MONITORAGGIO)
        # metto in ascolto la socket
        socket_server_monitoraggio.listen()
        while True:  # qui deve essere messo un shutdown
            # acetto le connessioni in entrata con il load balancer
            socket_lb_monitoraggio, address_lb_monitoraggio = socket_server_monitoraggio.accept()
            # richiamo la funzione che moniotra il carico del server
            notifica_sovraccarico = self.monitoraggio_carico_server(socket_lb_monitoraggio)
            # invio la percentuale di cpu al load balancer
            socket_lb_monitoraggio.sendall(notifica_sovraccarico.encode('utf-8'))
            socket_lb_monitoraggio.close()
            time.sleep(1)
        socket_server_monitoraggio.close()

    def monitoraggio_carico_server(self, socket_lb_monitoraggio):
        # controllo il carico della cpu per il server ogni secondo
        process = psutil.Process()
        memory_info = process.memory_info()

        # Memoria virtuale totale utilizzata dal processo (in byte)
        virtual_memory_used = memory_info.vms
        # se il carico della cpu è maggiore del limite, il server è sovraccarico
        if virtual_memory_used > self.LIMITE_CPU:
            self.SOVRACCARICO = "Sovraccarico"
        # altrimenti il server non è sovraccarico
        else:
            self.SOVRACCARICO = "Non sovraccarico"
        return self.SOVRACCARICO



    def esegui_comandi(self, comando, client_socket):
        # creo due valori random A e B che servono per i calcoli
        A = random.randint(1, 50)
        B = random.randint(1, 50)
        if comando == "somma":
            risultato = A + B
        if comando == "sottrazione":
            risultato = A - B
        if comando == "moltiplicazione":
            risultato = A * B
        if comando == "divisione":
            risultato = A / B
        soluzione = {'A': A,
                     'B': B,
                     'operazione': comando,
                     'risultato': risultato}
        return soluzione

    # MANCA L'ATTRIBUTO CHE INVIA LA SOLUZIONE DEI COMANDI AL CLIENT

if __name__ == "__main__":
    server = server()
    server.socket_server()