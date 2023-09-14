
import socket
import pickle

class LoadBalancer(object):
    def __init__(self):
        self.balancer_socket = None
        self.port = 60003  # porta in cui si mette in ascolto il server
        self.ip = '127.0.0.1'
        self.clients=[]
        self.client_socket=None

    def creo_socket_loadBalancer(self):
        self.balancer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Binding della socket all'host e alla porta
        self.balancer_socket.bind((self.ip, self.port))
        self.balancer_socket.listen()
        print("Server di load balancing in ascolto su {}:{}".format(self.ip, self.port))

    def connetto_il_client(self):
        # Accetta le connessioni in entrata
        self.client_socket, client_ip = self.balancer_socket.accept()
        # Aggiunge il client alla lista dei client connessi
        self.clients.append(self.client_socket)
        # Commento di riuscita connessione con il client
        print("Connessione accettata da {}:{}".format(client_ip[0], client_ip[1]))

    def ricevo_dati_dal_client(self):
        # Ricevi l'immagine serializzata
        image_data = b''
        while True:
            data = self.client_socket.recv(4096)
            if not data:
                break
            # file.write(data)
            # received_bytes += len(data)

        # Chiudi il socket del client
        self.client_socket.close()
        # Chiudi il socket del server
        self.balancer_socket.close()

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
    while True:
        load.connetto_il_client()
        load.ricevo_dati_dal_client()