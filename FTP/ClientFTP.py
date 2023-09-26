import socket
import sys
import os
import threading
import random
import time
import json

class Client(object):
    def __init__(self):
        self.loadBalancer_ip = "127.0.0.1"
        self.loadBalancer_port = "60004"
        self.filepath = None
        self.client_socket = None
        self.file_da_inviare = []
        self.counter_richieste = 0


    def avvio_client(self):
        """
        Metodo che avvia il client e i thread di invio file e ricezione delle risposte
        :return: None

        """
        self.avvio_client_socket()
        interfaccia = threading.Thread(target=self.interfaccia_utente)
        invio_file_al_loadbalancer = threading.Thread(target=self.invia_file_al_loadbalancer)
        #ricevi_risposta = threading.Thread(target=self.ricevi_dati_dal_loadbalancer)
        interfaccia.start()
        invio_file_al_loadbalancer.start()
        #ricevi_risposta.start()
        interfaccia.join()
        invio_file_al_loadbalancer.join()
        #ricevi_risposta.join()


    def avvio_client_socket(self):
        """
        Metodo che avvia la socket del client, e la connette al load balancer

        :return: None
        """
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(("127.0.0.1", 60002))
            print(f"Connessione al server {self.loadBalancer_ip}:{self.loadBalancer_port} stabilita.")
        except:
            print(f"Errore durante la connessione al server: {socket.error}")
            sys.exit(1)


    def interfaccia_utente(self):
        """
        Metodo di interfaccia con l'utente, che richiede in input il nome del file da inviare
        :return: None
        """
        while True:
            time.sleep(2)
            # Creo una lista con tutti i nomi dei file contenuti all'interno della cartella indata
            lista_file = os.listdir('./file/')
            print("La lista dei file disponibili è: ", lista_file)
            if len(lista_file) == 0:  # se la cartella è vuota blocca il codice e restituisce l'errore
                raise Exception("La cartella non ha file al suo interno.")

            comando = input(" Digita il comando:  ")
            if comando == 'exit':  # se inserisco exit, si chiude la connessione
                print("Chiusura della connessione con il server...")
                break
            if comando == 'FTP':
                try:
                    numero_file = int(input('Inserisci il numero di file da trasferire: '))   #inserisco numero file da inviare
                    for numero in range(numero_file):   #itero per un numero di volte pari al numero_file
                        nome_file_scelto = self.scegli_file_random()
                        filepath = './file/' + nome_file_scelto
                        self.file_da_inviare.append(filepath)
                except Exception as e:
                    print("Errore nella scrittura dell'input; riprova: ", e)
            else:
                print("Errore nella scrittura dell'input; riprova: ", e)




    def scegli_file_random(self):
        """
        Metodo che sceglie randomicamente un file dalla lista dei file considerata

        :return: file_casuale

        """
        # stampo la lista dei file fra cui scegliere
        lista_file = os.listdir('./file/')
        # scelgo casualmente uno fra i file nella lista
        file_casuale = random.choice(list(lista_file))

        return file_casuale

    def invia_file_al_loadbalancer(self):
        """
        Metodo che invia il file JSON preso in input al load balancer

        :return: None
        """
        try:
            while True:
                if len(self.file_da_inviare) != 0:
                    filepath = self.file_da_inviare[0]
                    self.file_da_inviare.pop(0)

                    # Apro il file JSON e lo converto in un dizionario
                    with open(filepath, 'r', encoding='utf-8') as file_json:
                        json_data = json.load(file_json)
                    #aggiungo una chiave che identifica il tipo di richiesta
                    json_data["request_type"]='file_di_testo'
                    #converto in una stringa di modo che possa eesere mandato attraverso la socket
                    json_data_to_send=json.dumps(json_data)
                    #invio il file json formattato come una stringa
                    self.client_socket.send(json_data_to_send.encode())  
                    time.sleep(0.3)
                    print(f"File JSON inoltrato al load balancer: \n", filepath)
                    self.counter_richieste += 1
        except socket.error as error:
            print(f"Errore di comunicazione con il loadbalancer: {error}")
            sys.exit(1)


    def ricevi_dati_dal_loadbalancer(self):
        """
        Metodo che riceve mette la socket in ascolto per ricevere i messaggi dal load balancer

        :return: None
        """
        try:
            while True:
                message_from_load = self.client_socket.recv(1024).decode("utf-8")
                self.counter_richieste -= 1
                print(message_from_load)
        except socket.error as error:
            print(f"Impossibile ricevere dati dal loadbalancer: {error}")
            sys.exit(1)




if __name__ == "__main__":
    client = Client()
    client.avvio_client()
