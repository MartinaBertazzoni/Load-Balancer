import sys
import socket
import random
import threading
import os


# commento per provare il commit


# creata la classe client per far accedere i thread agli attributi
class client(object):

    def __init__(self):
        """
        Costruttore della classe client
        """
        # stack dove vengono inseriti i comandi svolgere
        self.comandi = []
        # variabile che conta il numero richieste inviate e che devono ricevere risposta
        self.counter_richieste = 0
        # flag che mi dice se chiudere il socket
        self.chiusura = False
        self.name_client = None
        self.file_path_risultati = "./risultati.txt"

    def avvio_client(self):
        """
        Funzione che avvia e chiude tre thread:
        1.interfaccia che prende da input i comandi e li inserisce nella lista self.comandi
        2.thread che invia i comandi al load balancer
        3.thread che rimane in ascolto per ricevere le risposte delle richieste inviate
        """
        # controllo se il file dei risultati esiste; se non è esiste, lo creo
        # self.verifica_e_crea_file()
        # # controllo se il file dei risultati è vuoto; se no, lo svuoto
        # if not self.is_file_empty():
        #     self.svuota_file()
        # self.name_client=input("Inserisci il nome del Client connesso: ")

        client_socket = self.connessione_al_loadbalancer()
        interfaccia = threading.Thread(target=self.interfaccia_client)
        invio_richieste = threading.Thread(target=self.invia_richieste_al_loadbalancer, args=(client_socket,))
        ricevi_risposte = threading.Thread(target=self.ricezione_risposta, args=(client_socket,))
        interfaccia.start()
        invio_richieste.start()
        ricevi_risposte.start()
        interfaccia.join()
        invio_richieste.join()
        ricevi_risposte.join()

    def connessione_al_loadbalancer(self):
        """
        Funzione che collega il client al loadbalancer attraverso il socket.
        """
        # impostazione dell'ip del loadBalancer
        loadBalancer_ip = "127.0.0.1"
        # impostazione della porta dove è in ascolto il loadBalancer
        loadBalancer_port = "5006"

        try:
            # creo una socket client
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(client_socket)
            print(loadBalancer_ip)
            # client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # connetto il client con il loadBalancer
            # client_socket.connect((loadBalancer_ip, loadBalancer_port))
            client_socket.connect(("127.0.0.1", 60002))

            print(f"Connessione al server {loadBalancer_ip}:{loadBalancer_port} stabilita.")
            # DEVO RICHIAMARE COME FUNZIONE L'INTERFACCIA_CON_LOADBALANCER()
            # interfaccia_con_loadbalancer(client_socket)
            # return client_socket
            return client_socket
        except:
            print(f"Errore durante la connessione al server: {socket.error}")
            print("Sto uscendo...")
            sys.exit(1)

    def interfaccia_client(self):
        """
        Funzione che simula una interfaccia che richiede i comandi da svolgere
        """
        while True:
            # richiede il comando da terminale
            comando = input(" Digita il comando:  ")
            # inserisco il comando dentro la lista dei comandi da svolgere
            if comando == 'exit':
                self.comandi.append(comando)
                print("Chiusura della connessione con il server...")
                break
            if comando == 'random':
                # self.comandi.pop(0)
                num_richieste = int(input("Digita il numero di richieste randomiche da creare:  "))
                for numero in range(num_richieste):
                    richiesta = self.crea_comando_random()
                    print(richiesta)
                    self.comandi.append(richiesta)
            else:
                self.interfaccia_client()
                self.comandi.append(comando)

    def invia_richieste_al_loadbalancer(self, client_socket):
        """
        Funzione che invia i comandi al loadBalancer (connessione TCP e socket) e riceve le risposte del loadBalancer

        Returns
        -------
        None.

        """
        try:
            while True:
                # controllo se la lista dei comandi è vuota, se lo è assegno il comandi 'continua' che fa scorrere continuamente il thread
                if len(self.comandi) != 0:
                    # assegno il primo comando
                    comando = self.comandi[0]
                    self.comandi.pop(0)
                else:
                    comando = "continue"
                # se il comando è exit si manda il messaggio di chiusura al loadbalancer
                if comando == 'exit':
                    # imposto la flag di chiusura del client
                    self.chiusura = True
                    # Copyright owner Martina Bertazzzoni(feat. Antonio Spampinato)
                    client_socket.send(comando.encode())
                    self.counter_richieste += 1
                    print("Chiusura della connessione con il server...")
                    break
                # se il comando è 'continue' faccio continuare a scorrere il thread
                elif comando == "continue":
                    continue
                else:
                    # Invia il comando al server e aumento il numero di richieste
                    comando_con_slash="/"+comando
                    client_socket.send(comando_con_slash.encode())
                    self.counter_richieste += 1
        except socket.error as error:
            print(f"Errore di comunicazione con il server: {error}")
            sys.exit(1)

    def crea_comando_random(self):
        """
        Funzione che crea richieste/comandi random.
        Ad esempio, possiamo creare comandi random di calcolo; il comando scelto randomicamente verrà quindi
        inviato al loadBalancer, che a sua volta lo inoltrerà ad un server

        Returns: comando
        -------
        """
        # creo una lista di possibili richieste
        comandi_possibili = ["somma", "sottrazione", "moltiplicazione", "divisione"]
        # scelgo casualmente uno fra i comandi dalla lista dei comandi
        comando_casuale = random.choice(list(comandi_possibili))

        return comando_casuale

    def ricezione_risposta(self, client_socket):
        try:
            while True:
                # appena finisce di ricevere richieste e l'ultima richiesta è stata 'exit' chiude la socket
                if self.counter_richieste <= 0 | self.chiusura == True:
                    print('connessione chiusa')
                    client_socket.close()
                    break
                else:
                    message = client_socket.recv(1024).decode("utf-8")
                    # RICHIAMO METODO CHE SALVA I RISULTATI IN UN FILE
                    #self.creo_file_risposta(message)
                    print(message)
                    self.counter_richieste -= 1
        except:
            print("Vi è stato un errore")



    # def creo_file_risposta(self, risultato):
    #     """
    #     Creo un file con le risposte di tutte le richieste
    #
    #     :param risultato:
    #     :return:
    #     """
    #     with open('risultati.txt', 'a') as file:
    #         file.write(self.name_client + " " + risultato + "\n")
    #
    # def is_file_empty(self):
    #     """ Metodo che verifica se il contenuto del file è vuoto
    #         restituirà la dimensione del file in byte. Se il file è vuoto, la dimensione
    #         sarà 0, quindi la funzione is_file_empty restituirà True.
    #         Altrimenti, se il file ha del contenuto, restituirà False."""
    #     return os.path.getsize(self.file_path_risultati) == 0
    #
    # def svuota_file(self):
    #     """
    #     Metodo che elimina il contenuto del file
    #     return: None
    #     """
    #     with open(self.file_path_risultati, 'w') as file:
    #         pass
    #
    # def verifica_e_crea_file(self):
    #     if not os.path.exists(self.file_path_risultati):
    #         # Se il file non esiste, crealo
    #         with open(self.file_path_risultati, 'w') as file:
    #             pass


if __name__ == "__main__":
    client = client()
    client.avvio_client()