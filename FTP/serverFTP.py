import socket
import threading
import json
import os
import time

class Server(object):

    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = 5001
        self.server_socket = None
        self.balancer_socket = None


    def avvio_server(self):

        self.svuota_directory_json_files() #aggiungi creazione file se non è presente!!!!
        self.creo_socket_server()
        self.connetto_il_loadbalancer()

        # Ho bisogno di 2 thread:
        # 1) Connetto il loadbalancer (il server accetta più richieste)
        # 2) Ricevi file
        # Il fatto che questi due thread siano indipendenti, vuol dire che il server continua a ricevere richieste quando potrebbe
        # star finendo di elaborarne un'altra.



    def creo_socket_server(self):
        """
        Funzione che crea la socket del server e crea un thread che rimane in ascolto per ricevere i comandi dal load balancer
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
        Metodo che connette il loadbalancer
        :return: None
        """
        try:
            while True:
                # Accetta le connessioni in entrata
                self.balancer_socket, balancer_ip = self.server_socket.accept()   #accetto le richieste (Accetta ogni volta che ho una richiesta)
                ricezione_dati = threading.Thread(target=self.ricevo_file_dal_loadbalancer)
                ricezione_dati.start()
                ricezione_dati.join()
                # Serve thread per far svolgere i compiti al server. Ad esempio, vogliamo che il server
                # conti le lettere "A" contenute nel testo

                # Quindi ho 1 thread per accettare le richieste,
        except Exception as e:
            print("Errore durante la connessione con il loadbalancer:", e)


    def ricevo_file_dal_loadbalancer(self):
        try:
            while True:
                file= self.balancer_socket.recv(4096).decode("utf-8")
                if not file:
                    break

                # Decodifica il file JSON e lo mette in forma di dizionario
                json_data = json.loads(file)
                # Estrai il titolo e il contenuto dal file JSON
                titolo = json_data.get("titolo", "")
                contenuto = json_data.get("contenuto", "")
                print(f" File ricevuto correttamente dal server: {titolo}")

                # invia notifica al load balancer di avvenuta ricezione del file
                self.invia_risposte_al_loadbalancer(titolo)

                # salvo il contenuto del file
                self.salvo_file_ricevuto(titolo, contenuto)
                print(f"File {titolo} salvato correttamente ")

        except Exception as e:
            print("Errore durante la comunicazione con il loadbalancer:", e)
        finally:
            self.balancer_socket.close()


    def salvo_file_ricevuto(self, titolo, contenuto):

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


    def invia_risposte_al_loadbalancer(self, titolo):
        """
                Metodo che invia la risposta al load balancer di avvenuta ricezione del file

                :param balancer_socket: socket del load balancer
                :param titolo: titolo del file ricevuto
                :return: None

                """

        message_to_client = f" File ricevuto correttamente dal server 1: {titolo}"
        self.balancer_socket.send(message_to_client.encode("utf-8"))



if __name__ == "__main__":
    server=Server()
    server.avvio_server()

