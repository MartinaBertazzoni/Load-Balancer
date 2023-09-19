import sys
import socket
import threading
import json

class LoadBalancer(object):
    def __init__(self):
        self.balancer_socket = None
        self.port = 60003  # porta in cui si mette in ascolto il server
        self.ip = '127.0.0.1'
        self.clients=[]
        self.SERVERS = ["127.0.0.1", "127.0.0.1", "127.0.0.1"]
        self.PORTS = [5007, 5008, 5009]
        self.CURRENT_SERVER_INDEX = 0
        # indice della porta del server a cui il LB si sta interfacciando
        self.CURRENT_SERVER_PORT_INDEX = 0
        # lista che contiene le flag per il monitoraggio dei server
        self.SERVER_FLAGS = [False] * len(self.SERVERS)
        # lista che contiene le flag per il monitoraggio del sovraccarico dei server
        self.SERVER_SOVRACCARICO_FLAGS = [False] * len(self.SERVERS)
        # lista che contiene i processi attivi
        self.PROCESSI_ATTIVI = []


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
            server_address = "127.0.0.1"
            server_port = 5007
            # creo una socket per la connessione con il server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # mi connetto con il server
            server_socket.connect((server_address, server_port))

            #DA IMPLEMENTARE
            with open(self.filepath, 'r', encoding='utf-8') as file:
                json_data = file.read()
            server_socket.send(json_data.encode("utf-8"))

            # ricevo risposte dai server
            risposta_dal_server = threading.Thread(target=self.ricevi_risposta_server, args=(server_socket,client_socket))
            risposta_dal_server.start()
            risposta_dal_server.join()
        except socket.error as error:
            print(f"Errore di comunicazione con il server: {error}")
            sys.exit(1)


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
    load.creo_socket_loadBalancer()
    load.connetto_il_client()