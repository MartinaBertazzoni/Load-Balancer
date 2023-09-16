import os.path
import shutil
import socket
import threading
import sys
import time
import psutil


class Server(object):

    def _init_(self):
        """
        Costruttore della classe server
        """
        # indirizzo e porta del server
        self.ADDRESS = ("127.0.0.1", 5007)
        # formato del messaggio
        self.FORMAT = 'utf-8'
        # limite della cpu per il server
        self.LIMITE_CPU = 80
        # variabile di sovraccarico del server
        self.SOVRACCARICO = False
        # indirizzo e porta del load balancer
        self.LB_ADDRESS = ("127.0.0.1", 60003)
        # variabile che ospiterà la socket del load balancer
        self.LB = None
        # variabile che contiene il percorso della cartella dove verranno trasferiti i file
        self.CARTELLA_DESTINAZIONE = "./archivio_server1_ftp"




    def socket_server(self):
        """
        Funzione che crea la socket del server e che si conette con il load balancer
        """
        # creo una socket server
        print("[STARTING] Il server sta partendo.")
        print()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # collego la socket al server
        server_socket.bind(self.ADDRESS)
        time.sleep(0.5)
        # metto in ascolto il server
        server_socket.listen()
        print(f"[LISTENING] Server in ascolto su {self.ADDRESS[0]}:{self.ADDRESS[1]}")
        # mi preparo ad accettare la connessione con il load balancer
        try:
            # accetto le connessioni in entrata con il load balancer
            self.LB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.LB.connect(self.LB_ADDRESS)
            print("[CONNECTED] Connessione con il load balancer stabilita")
            # creo il thread per il monitoraggio del carico della cpu del server
            thread_monitoraggio_carico_server = threading.Thread(target=self.monitoraggio_carico_server)
            thread_monitoraggio_carico_server.start()
            # creo il thread per la ricezione del file dal load balancer
            thread_ricevi_dal_loadbalancer = threading.Thread(target=self.ricevi_dal_loadbalancer)
            thread_ricevi_dal_loadbalancer.start()
            thread_ricevi_dal_loadbalancer.join()
        # se qualcosa va storto, sollevo una eccezione e il server si chiude
        except:
            print("Errore di connessione con il load balancer")
            print("Il server si chiude...")
            # chiudo la socket del server
            server_socket.close()
            # termino il programma
            sys.exit()


    def notifica_load_balancer(self, notifica):
        """
        Funzione che notifica il load balancer delle varie informazioni per il monitraggio e il funzionamento del server stesso:
        questo è un thread sempre attivo
        Returns
        -------

        """
        try:
            # mi connetto con il load balancer
            self.LB.connect(self.LB_ADDRESS)
            # invio la notifica
            self.LB.sendall(notifica.encode('utf-8'))
        except:
            print("Errore nell'invio della notifica al load balancer")
            print("Il server si chiude...")
            sys.exit()




    def monitoraggio_carico_server(self):
        """
        Funzione che monitora il carico della cpu del server
        Returns
        -------

        """
        while True:
            # controllo il carico della cpu per il server ogni secondo
            cpu_percent = psutil.cpu_percent(interval=1)
            # se il carico della cpu è maggiore del limite, il server è sovraccarico
            if cpu_percent > self.LIMITE_CPU:
                self.SOVRACCARICO = True
                notifica = "Sovraccarico"
                self.notifica_load_balancer(notifica)
            # altrimenti il server non è sovraccarico
            else:
                self.SOVRACCARICO = False
                notifica = "Non sovraccarico"
                self.notifica_load_balancer(notifica)



    def ricevi_dal_loadbalancer(self):
        try:
            while True:
                # ricevo il nome del file FTP dal load balancer
                nome_file = self.LB.recv(1024).decode('utf-8')
                # stampo un messaggio che informa della ricezione del nome del file
                print(f"[RECV] {nome_file} ricevuto dal load balancer")
                # controllo se la cartella di destinazione esiste, altrimenti la creo
                if not os.path.exists(self.CARTELLA_DESTINAZIONE):
                    os.makedirs(self.CARTELLA_DESTINAZIONE)
                # apro il file in modalità scrittura binaria
                file = open(self.CARTELLA_DESTINAZIONE + nome_file, "wb")
                # ricevo i dati del file dal load balancer
                data = self.LB.recv(1024).decode('utf-8')
                # stampo un messaggio che informa della ricezione dei dati del file
                print(f"[RECV] dati del file ricevuti")
                # scrivo i dati del file nel file --> BISOGNA CONTROLLARE SE IL FILE VIENE CREATO
                file.write(data)
                # mando un messaggio di conferma della ricezione dei dati del file al load balancer
                self.LB.sendall("File ricevuto".encode('utf-8'))
                # chiudo il file
                file.close()
                # Sposta il file nella cartella di destinazione
                # percorso_file_destinazione = os.path.join(self.CARTELLA_DESTINAZIONE, nome_file)
                # shutil.move(nome_file, percorso_file_destinazione)
                # chiudo la connessione con il load balancer
                self.LB.close()
                # stampo un messaggio che informa della chiusura della connessione con il load balancer
                print(f"[CLOSED] Connessione con il load balancer chiusa")
                print()
        except:
            print("Errore nella ricezione del file dal load balancer")
            self.LB.close()
            print("Il server si chiude...")
            sys.exit()






    def invia_al_loadbalancer(self):
        pass