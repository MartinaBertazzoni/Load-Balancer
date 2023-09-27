import socket
import threading
import json
import os
import time
import psutil

class Server(object):

    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = 5001
        self.server_socket = None
        self.active_requests=[]
        self.SOVRACCARICO=False
        self.LIMITE_CPU_percentuale=0.14#la percentuale di utilizzo prima delle richieste è 0.054
        monitoraggio_status=threading.Thread(target=self.monitoraggio_carico_server)
        monitoraggio_status.daemon=True
        monitoraggio_status.start()


    def avvio_server(self):
        """
        Metodo che richiama i metodi per avviare il server; in particolare, svuota la directory di salvataggio dei file,
        crea la socket del server, e connette il server al loadbalancer

        :return: None
        """

        self.svuota_directory_json_files()
        self.creo_socket_server()
        self.connetto_il_loadbalancer()


    def creo_socket_server(self):
        """
        Metodo che crea la socket del server e la mette in ascolto

        :return: None
        """
        # creo una socket server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # collego la socket al server
        self.server_socket.bind((self.ip, self.port))
        # metto in ascolto il server
        self.server_socket.listen()
        print(f"Server in ascolto su {self.ip}:{self.port}")


    def connetto_il_loadbalancer(self):
        """
        Metodo che connette il server al loadbalancer
        :return: None
        """
        try:
            while True:
                self.server_socket.settimeout(1)
                try:
                    # Accetta le connessioni in entrata
                    #l'ho chiamato richiesta_socket, ma sarebbe la socket della richiesta
                    richiesta_socket, richiesta_ip = self.server_socket.accept()   #accetto le richieste (Accetta ogni volta che ho una richiesta)
                    self.active_requests.append(richiesta_socket)
                    ricezione_dati = threading.Thread(target=self.ricevo_file_dal_loadbalancer, args=(richiesta_socket,))
                    ricezione_dati.start()
                    # Serve thread per far svolgere i compiti al server. Ad esempio, vogliamo che il server
                    # conti le lettere "A" contenute nel testo

                    # Quindi ho 1 thread per accettare le richieste,
                except socket.timeout:
                    continue
                if richiesta_socket not in self.active_requests:
                    ricezione_dati.join()
        except Exception as e:
            print("Errore durante la connessione con il loadbalancer:", e)


    def ricevo_file_dal_loadbalancer(self,richiesta_socket):
        try:
            while True:
                file= richiesta_socket.recv(4096).decode("utf-8")
                if not file:
                    break
                # Decodifica il file JSON e lo mette in forma di dizionario
                json_data = json.loads(file)
                #capisco il tipo di rischiesta
                request_type=json_data.get("request_type","")
                if request_type=='file_di_testo':
                    # Estrai il titolo e il contenuto dal file JSON
                    titolo = json_data.get("titolo", "")
                    contenuto = json_data.get("contenuto", "")
                    # invia notifica al load balancer di avvenuta ricezione del file
                    #self.invia_risposte_al_loadbalancer(titolo,richiesta_socket)
                    self.conta_a(contenuto)
                    # salvo il contenuto del file
                    self.salvo_file_ricevuto(titolo, contenuto)
                    print(f"File {titolo} salvato correttamente ")
                else:
                    status=bytes([self.SOVRACCARICO])
                    richiesta_socket.send(status)
                    break
        except Exception as e:
            print("Errore durante la comunicazione con il loadbalancer:", e)
        finally:
            self.active_requests.remove(richiesta_socket)
            richiesta_socket.close()

    def conta_a(self, contenuto):
        """
        Metodo che conta il numero di lettere A contenute all'interno di un testo

        :param contenuto: contenuto del file ricevuto
        :return: None
        """
        # Funzione che ricerca le a in contenuto, simulando una situazione di sovraccarico per il server.
        count_a = 0
        #ho utilizzato range di len, perchè il timesleep non simula il carico. Infatti mette a dormire il processo e quindi non grava sulla cpu
        for i in range(len(contenuto)):
            if contenuto[i] == 'a' or contenuto[i]== 'A':
                count_a += 1
            time.sleep(0.5)
            
    
    def salvo_file_ricevuto(self, titolo, contenuto):
        """
        Metodo che salva il file ricevuto all'interno della cartella json_files_1

        :param titolo: titolo del file
        :param contenuto: contenuto del file
        :return: None
        """

        # Genera un nome di file univoco basato su un timestamp
        timestamp = str(int(time.time()))  # Converti il timestamp in una stringa
        json_filename = f"json_files_1/{timestamp}_{titolo}.json"

        # Verifica se la directory "json_files" esiste, altrimenti creala
        if not os.path.exists("json_files_1"):
            os.makedirs("json_files_1")
            # salvo il contenuto del file
            with open(json_filename, "w", encoding="utf-8") as json_file:
                json_file.write(contenuto)
        else:
            # salvo il contenuto del file in un nuovo file all'interno della directory json_files
            with open(json_filename, "w", encoding="utf-8") as json_file:
                    json_file.write(contenuto)


    def svuota_directory_json_files(self):
        """
        Metodo che svuota il contenuto della directory "json_files_1" ogni volta che si riavvia il codice
        :return: None
        """
        json_files_directory = "json_files_1"
        try:
            # Crea la cartella se non esiste
            if not os.path.exists(json_files_directory):
                os.makedirs(json_files_directory)
            for filename in os.listdir(json_files_directory):
                file_path = os.path.join(json_files_directory, filename)
                if os.path.isfile(file_path) and filename.endswith(".json"):
                    os.remove(file_path)
        except Exception as e:
            print(f"Errore durante lo svuotamento della directory JSON: {e}")


    def invia_risposte_al_loadbalancer(self, titolo,richiesta_socket):
        """
        Metodo che invia la risposta al load balancer di avvenuta ricezione del file

        :param balancer_socket: socket del load balancer
        :param titolo: titolo del file ricevuto
        :return: None

        """

        message_to_client = f" File ricevuto correttamente dal server 1: {titolo}"
        richiesta_socket.send(message_to_client.encode("utf-8"))


    def monitoraggio_carico_server(self):
        """
        Metodo che monitora continuamente il carico della cpu del server. Se la memoria virtuale utilizzata dal processo
        supera il limite imposto, la flag SOVRACCARICO diventa True
        :return: None
        """
        
        while True:
            process = psutil.Process(os.getpid())  # Get the current process (your script)
            memory_info = process.memory_info()
            # Memoria virtuale totale utilizzata dal processo (in byte)
            self.virtual_memory_used = memory_info.vms
            # Percentage of total system memory used by the process
            memory_percent = (memory_info.vms / psutil.virtual_memory().total) * 100
            print(memory_percent)
            # se il carico della cpu è maggiore del limite, il server è sovraccarico
            if memory_percent > self.LIMITE_CPU_percentuale:
                self.SOVRACCARICO = True
            else:
                self.SOVRACCARICO = False
            

if __name__ == "__main__":
    server=Server()
    server.avvio_server()

