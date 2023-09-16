import sys
import socket
import threading
import time

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
            except Exception as e:
                print("Errore durante la comunicazione con il client:", e)


    def ricevo_file_dal_client(self, client_socket):
        try:
            while True:
                file = client_socket.recv(1024).decode("utf-8")
                print(" Ho ricevuto il file: ", file)
                message_to_client = f" File ricevuto correttamente dal load balancer: {file}"
                client_socket.send(message_to_client.encode("utf-8"))
                # #creo un thread che invia i file ai server
                # invia_file_ai_server=threading.Thread(target=self.invia_ai_server, args=(file,))
                # invia_file_ai_server.start()
                # invia_file_ai_server.join()
                # risposta_dal_server = threading.Thread(target=self.ricevi_risposta_server())
                # risposta_dal_server.start()
                # risposta_dal_server.join()

        except Exception as e:
            print("Errore durante la comunicazione con il client:", e)


    # def invia_ai_server(self, file):
    #     try:
    #         self.balancer_socket.send(file.encode("utf-8"))
    #         print("File inoltrato al server ")
    #     except socket.error as error:
    #         print(f"Errore di comunicazione con il loadbalancer: {error}")
    #         sys.exit(1)
    #     pass
    #
    # def ricevi_risposta_server(self):
    #     try:
    #         message_from_server = self.balancer_socket.recv(1024).decode("utf-8")
    #         print(message_from_server)
    #     except socket.error as error:
    #         print(f"Impossibile ricevere dati dal loadbalancer: {error}")
    #         sys.exit(1)


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