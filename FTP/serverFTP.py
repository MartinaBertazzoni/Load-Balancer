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
        self.active_requests = []
        self.SOVRACCARICO = False
        self.directory_name = "json_files_1"  # directory di salvataggio dei file
        self.LIMITE_CPU_percentuale = None  # valore che si aggiorna in base alla percentuale di cpu calcolata all'avvio
        monitoraggio_status = threading.Thread(target=self.monitoraggio_carico_server)
        monitoraggio_status.daemon = True
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
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen()
        print(f"Server in ascolto su {self.ip}:{self.port}")

    def connetto_il_loadbalancer(self):
        """
        Metodo che connette il server al loadbalancer e avvia il thread per ricevere e elaborare i dati inviati
        dal loadbalancer
        :return: None
        """
        try:
            while True:
                self.server_socket.settimeout(1)
                try:
                    # Accetta le connessioni in entrata; richiesta socket indica che è la socket delle richieste
                    richiesta_socket, richiesta_ip = self.server_socket.accept()
                    self.active_requests.append(richiesta_socket)
                    # avvio un thread per gestire ogni richiesta ricevuta dal loadbalancer
                    ricezione_dati = threading.Thread(target=self.gestione_richiesta, args=(richiesta_socket,))
                    ricezione_dati.start()
                except socket.timeout:
                    continue
                if richiesta_socket not in self.active_requests:
                    ricezione_dati.join()
        except Exception as e:
            print("Errore durante la connessione con il loadbalancer:", e)

    def gestione_richiesta(self, richiesta_socket):
        """
        Metodo che prende in ingresso la socket della richiesta corrente, riceve e legge il file, chiama il metodo
        per contare le lettere "a" all'interno del testo del file, e infine lo salva
        nella directory
        :param richiesta_socket: socket da cui riceve la richiesta corrente
        :return: None

        """
        try:
            file = richiesta_socket.recv(4096).decode("utf-8")
            # Decodifica il file JSON e lo mette in forma di dizionario
            json_data = json.loads(file)
            request_type = json_data.get("request_type", "")  # estraggo il tipo di rischiesta
            if request_type == 'file_di_testo':
                # estraggo titolo, contenuto, e numero di richiesta dal file
                titolo, contenuto, numero_richiesta = self.estraggo_caratteristiche_file(json_data)
                self.conta_a(contenuto)
                self.salvo_file_ricevuto(titolo, contenuto, numero_richiesta)
                print(f"File {titolo} salvato correttamente ")
            else: # è una richiesta di stato
                status = bytes([self.SOVRACCARICO])
                richiesta_socket.send(status)
        except Exception as e:
            print("Errore durante la comunicazione con il loadbalancer:", e)
        finally:
            self.active_requests.remove(richiesta_socket)
            richiesta_socket.close()

    def estraggo_caratteristiche_file(self, json_data):
        """
        Estraggo dal file ricevuto il titolo, il contenuto e il numero di richiesta corrente
        :param json_data: dati json ricevuti
        :return:
        titolo
        contenuto
        numero_richiesta
        """
        titolo = json_data.get("titolo", "")
        contenuto = json_data.get("contenuto", "")
        numero_richiesta = json_data.get("numero_richiesta", "")
        return titolo, contenuto, numero_richiesta

    def conta_a(self, contenuto):
        """
        Metodo che conta il numero di lettere A contenute all'interno di un testo

        :param contenuto: contenuto del file ricevuto
        :return: None
        """
        count_a = 0
        for i in range(len(contenuto)):
            if contenuto[i] == 'a' or contenuto[i] == 'A':
                count_a += 1
            time.sleep(0.02)

    def salvo_file_ricevuto(self, titolo, contenuto, numero_richiesta):
        """
        Metodo che salva il file ricevuto all'interno della cartella json_files_1

        :param titolo: titolo del file
        :param contenuto: contenuto del file
        :return: None
        """
        # Genera un nome di file univoco utilizzando il numero della richiesta
        json_filename = f"{self.directory_name}/{numero_richiesta}_{titolo}"
        # Verifica se la directory "json_files" esiste, altrimenti creala
        if not os.path.exists(self.directory_name):
            os.makedirs(self.directory_name)
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
        try:
            # Crea la cartella se non esiste
            if not os.path.exists(self.directory_name):
                os.makedirs(self.directory_name)
            for filename in os.listdir(self.directory_name):
                file_path = os.path.join(self.directory_name, filename)
                if os.path.isfile(file_path) and filename.endswith(".json"):
                    os.remove(file_path)
        except Exception as e:
            print(f"Errore durante lo svuotamento della directory JSON: {e}")


    def monitoraggio_carico_server(self):
        """
        Metodo che monitora continuamente il carico della cpu del server. Se la memoria virtuale utilizzata dal processo
        supera il limite imposto, la flag SOVRACCARICO diventa True
        :return: None
        """
        # ottengo la percentuale di cpu utilizzata dal processo in fase di avvio
        starting_memory_percent = self.ottieni_cpu_utilizzata()
        self.LIMITE_CPU_percentuale = starting_memory_percent + 0.025
        while True:
            memory_percent = self.ottieni_cpu_utilizzata()
            # se il carico della cpu è maggiore del limite, il server è sovraccarico
            if memory_percent > self.LIMITE_CPU_percentuale:
                self.SOVRACCARICO = True
            else:
                self.SOVRACCARICO = False

    def ottieni_cpu_utilizzata(self):
        """
        Metodo che ottiene la percentuale di cpu utilizzata dal processo
        :return:
        memory_percent
        """
        process = psutil.Process(os.getpid())  # considero il processo corrente (script attuale)
        memory_info = process.memory_info()
        # percentuale della memoria totale del sistema utilizzata dal processo
        memory_percent = (memory_info.vms / psutil.virtual_memory().total) * 100
        return memory_percent


if __name__ == "__main__":
    server = Server()
    server.avvio_server()