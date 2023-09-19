import socket
import threading
import json
import os
import time

class Server(object):

    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = 5007
        self.server_socket = None


    def creo_socket_server(self):
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
        self.connetto_il_loadbalancer()


    def connetto_il_loadbalancer(self):
        while True:
            try:
                # Accetta le connessioni in entrata
                balancer_socket, balancer_ip = self.server_socket.accept()
                # Commento di riuscita connessione con il client
                print("Connessione accettata da {}:{}".format(balancer_ip[0], balancer_ip[1]))
                ricezione_dati = threading.Thread(target=self.ricevo_file_dal_loadbalancer, args=(balancer_socket,))
                ricezione_dati.start()
                ricezione_dati.join()
            except Exception as e:
                print("Errore durante la connessione con il loadbalancer:", e)


    def ricevo_file_dal_loadbalancer(self, balancer_socket):
        try:
            while True:
                file_name = balancer_socket.recv(4096).decode("utf-8")
                if not file_name:
                    break
                # Decodifica il file JSON
                json_data = json.loads(file_name)
                # Estrai il titolo e il contenuto dal file JSON
                titolo = json_data.get("titolo", "")
                contenuto = json_data.get("contenuto", "")
                print(f"Titolo ricevuto dal client: {titolo}")
                print(f"Contenuto ricevuto dal client: {contenuto}")
                # salvo il file ricevuto
                self.salvo_file_ricevuto(titolo, contenuto)
        except Exception as e:
            print("Errore durante la comunicazione con il loadbalancer:", e)
        finally:
            balancer_socket.close()

    def salvo_file_ricevuto(self, titolo, contenuto):
        # Verifica se la directory "json_files" esiste, altrimenti creala
        if not os.path.exists("json_files"):
            os.makedirs("json_files")
        else:
            # Genera un nome di file univoco basato su un timestamp
            timestamp = str(int(time.time()))  # Converti il timestamp in una stringa
            json_filename = f"json_files/{timestamp}_{titolo}.json"

            # salvo il contenuto del file in un nuovo file all'interno della directory json_files
            with open(json_filename, "w", encoding="utf-8") as json_file:
                    json_file.write(contenuto)

    def invia_risposte_al_loadbalancer(self):

        pass



if __name__ == "__main__":
    server=Server()
    server.creo_socket_server()
