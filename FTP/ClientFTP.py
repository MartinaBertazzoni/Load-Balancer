import socket
import sys
import os
import threading
import time


class Client(object):

    def __init__(self):
        self.loadBalancer_ip = "127.0.0.1"
        self.loadBalancer_port = "60003"
        self.filepath = None
        self.client_socket = None


    def avvio_client(self):
        self.avvio_client_socket()
        interfaccia = threading.Thread(target=self.interfaccia_utente())
        interfaccia.start()



    def avvio_client_socket(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(("127.0.0.1", 60003))
            print(f"Connessione al server {self.loadBalancer_ip}:{self.loadBalancer_port} stabilita.")
            return self.client_socket
        except:
            print(f"Errore durante la connessione al server: {socket.error}")
            sys.exit(1)


    def interfaccia_utente(self):

        while True:
            # Creo una lista con tutti i nomi dei file contenuti all'interno della cartella indata
            lista_file = os.listdir('./file/')
            print(lista_file)
            if len(lista_file) == 0:
                # se la cartella è vuota blocca il codice e restituisce l'errore
                raise Exception("La cartella non ha file al suo interno.")
            else:
                nomefile = str(input('Inserisci il nome del file da trasferire fra quelli elencati:  '))
                if nomefile == 'exit':
                    print("Chiusura della connessione con il server...")
                    break
                if nomefile in lista_file:
                    self.filepath = './file/' + nomefile
                    invio_richieste = threading.Thread(target=self.invia_file_al_loadbalancer)
                    invio_richieste.start()
                    invio_richieste.join()
                    ricevi_risposte_dal_load = threading.Thread(target=self.ricevi_dati_dal_loadbalancer())
                    ricevi_risposte_dal_load.start()
                    time.sleep(1)
                else:
                    self.interfaccia_utente()


    def invia_file_al_loadbalancer(self):
        try:
            # Apri il file JSON e leggine il contenuto come stringa
            with open(self.filepath, 'r', encoding='utf-8') as file:
                json_data = file.read()
            self.client_socket.send(self.filepath.encode())
            # Invia il file JSON come stringa codificata al load balancer
            self.client_socket.send(json_data.encode("utf-8"))
            print(f"File JSON inoltrato al load balancer")
            print(json_data)
        except socket.error as error:
            print(f"Errore di comunicazione con il loadbalancer: {error}")
            sys.exit(1)


    def ricevi_dati_dal_loadbalancer(self):
        try:
            message_from_load = self.client_socket.recv(1024).decode("utf-8")
            print(message_from_load)
        except socket.error as error:
            print(f"Impossibile ricevere dati dal loadbalancer: {error}")
            sys.exit(1)




if __name__ == "__main__":
    client = Client()
    client.avvio_client()