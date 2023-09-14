import socket

class Server(object):

    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = 5007
        self.server.socket=None

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


    def riceve_richieste_dal_loadbalancer(self):
        while True:
        # accetto le connessioni in entrata
            load_, load_ip = self.server_socket.accept()
        pass


    def invia_risposte_al_loadbalancer(self):
        pass



if __name__ == "__main__":
    server=Server()
    server.creo_socket_server()