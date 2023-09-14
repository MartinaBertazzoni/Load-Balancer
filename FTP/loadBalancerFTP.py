from PIL import Image
import socket
import pickle
import io

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
            image_data += data
            # Crea un oggetto BytesIO dalla variabile image_data
            image_io = io.BytesIO(image_data)
            # Apre l'immagine da BytesIO
            image = Image.open(image_io)
        return image

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
        immagine_ricevuta = load.ricevo_dati_dal_client()
        if immagine_ricevuta:
            immagine_ricevuta.show()