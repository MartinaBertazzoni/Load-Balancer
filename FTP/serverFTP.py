import socket
import threading
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


    def connetto_il_loadbalancer(self):
        while True:
            try:
                # Accetta le connessioni in entrata
                balancer_socket, balancer_ip = self.server_socket.accept()
                # Commento di riuscita connessione con il client
                print("Connessione accettata da {}:{}".format(balancer_ip[0], balancer_ip[1]))
                ricezione_dati = threading.Thread(target=self.ricevo_file_dal_loadbalancer, args=(balancer_socket,))
                ricezione_dati.start()
            except Exception as e:
                print("Errore durante la comunicazione con il client:", e)


    def ricevo_file_dal_loadbalancer(self, balancer_socket):
        try:
            while True:
                file = balancer_socket.recv(1024).decode("utf-8")
                print(" Ho ricevuto il file: ", file)
                message_to_client = f" File ricevuto correttamente dal load balancer: {file}"
                balancer_socket.send(message_to_client.encode("utf-8"))

        except Exception as e:
            print("Errore durante la comunicazione con il client:", e)




    def invia_risposte_al_loadbalancer(self):
        pass



if __name__ == "__main__":
    server=Server()
    server.creo_socket_server()
    server.connetto_il_loadbalancer()