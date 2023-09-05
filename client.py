import sys
import socket
import random
import threading
import time


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

    def avvio_client(self):
        
        """
        Metodo che avvia e chiude tre thread:
            1.thread interfaccia, che prende da input i comandi e li inserisce nella lista self.comandi
            2.thread invio_richieste, che invia i comandi al load balancer
            3.thread ricevi_risposte, che rimane in ascolto per ricevere le risposte delle richieste inviate

        Returns
        -------
        None.

        """
        client_socket = self.connessione_al_loadbalancer()
        interfaccia = threading.Thread(target=self.interfaccia_client)
        invio_richieste = threading.Thread(target=self.invia_richieste_al_loadbalancer, args=(client_socket,))
        ricevi_risposte = threading.Thread(target=self.ricezione_risposta, args=(client_socket,))
        interfaccia.start();
        invio_richieste.start();
        ricevi_risposte.start()
        interfaccia.join();
        invio_richieste.join();
        ricevi_risposte.join()

    def connessione_al_loadbalancer(self):
        """
        Metodo che crea la socket con il client e la collega al loadBalancer
        
        Returns
        -------
        None.

        """
        # impostazione dell'ip del loadBalancer
        loadBalancer_ip = "127.0.0.1"
        # impostazione della porta dove è in ascolto il loadBalancer
        loadBalancer_port = "5006"
        try:
            # creo una socket client
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(("127.0.0.1", 60002))
            print(f"Connessione al server {loadBalancer_ip}:{loadBalancer_port} stabilita.")
            return client_socket
        except:
            print(f"Errore durante la connessione al server: {socket.error}")
            sys.exit(1)
            

    def interfaccia_client(self):
        
        """
        Metodo di interfaccia con il client, che richiede in input il numero di richieste da effettuare al loadBalancer

        Returns
        -------
        richiesta: str
            comando randomico da inviare al loadBalancer
 
        """

        while True:
            #richiede il comando da terminale 
            comando = input(" Digita il comando:  ")
            #inserisco il comando dentro la lista dei comandi da svolgere
            if comando == 'random':
                #self.comandi.pop(0)
                num_richieste = int(input("Digita il numero di richieste randomiche da creare:  "))
                for numero in range(num_richieste):
                    richiesta = self.crea_comando_random()
                    time.sleep(0.30)
                    self.comandi.append(richiesta)
                print(self.comandi)
            else:
                self.comandi.append(comando)
            if comando == 'exit':
                self.comandi.append(comando)
                print("Chiusura della connessione con il server...")
                break

            
            

    def invia_richieste_al_loadbalancer(self, client_socket):
        
        """
        Metodo che invia i comandi al loadBalancer (connessione TCP e socket) 
        
        Parameters
        ----------
        client_socket: socket

        Returns
        -------
        None.
        
        """

        try:
            while True:
                # controllo che la lista dei comandi non sia vuota
                if len(self.comandi) != 0:
                    # assegno il primo comando
                    comando = self.comandi[0]
                    self.comandi.pop(0)
                    print(comando, self.comandi)
                    # se la lista dei comandi è vuota, assegno il comando 'continua' che fa scorrere continuamente il thread
                else:
                    comando="continue"
                # se il comando è exit si manda il messaggio di chiusura al loadbalancer
                if comando == 'exit':
                    #imposto la flag di chiusura del client
                    self.chiusura=True
                    #Copyright owner Martina Bertazzzoni(feat. Antonio Spampinato)
                    client_socket.send(comando.encode())
                    self.counter_richieste+=1
                    print("Chiusura della connessione con il server...")
                    break
                else:
                    # Invia il comando al server e aumento il numero di richieste
                    client_socket.send(comando.encode())
                    self.counter_richieste += 1
        except socket.error as error:
            print(f"Errore di comunicazione con il server: {error}")
            sys.exit(1)
            

    def crea_comando_random(self):
        
        """
        Metodo che crea richieste/comandi random.
        Ad esempio, possiamo creare comandi random di calcolo; il comando scelto randomicamente verrà quindi
        inviato al loadBalancer, che a sua volta lo inoltrerà ad un server

        Returns
        -------
        comando_casuale : str
         
        """
        
        # creo una lista di possibili richieste
        comandi_possibili = ["somma", "sottrazione", "moltiplicazione", "divisione"]
        # scelgo casualmente uno fra i comandi dalla lista dei comandi
        comando_casuale = random.choice(list(comandi_possibili))
        return comando_casuale


    def ricezione_risposta(self, client_socket):
        
        """
        
        Parameters
        ----------
        client_socket: socket

        Returns
        -------
        message : str
             risposta del loadBalancer
             
        """

        try:
            while True:
                # se smette di ricevere richieste o l'ultima richiesta è stata 'exit', chiude la socket
                if self.counter_richieste <= 0 | self.chiusura == True:
                    client_socket.close()
                    break
                else:
                    # riceve i messaggi, e diminuisce il contatore delle richieste
                    message = client_socket.recv(1024).decode("utf-8")
                    print(message)
                    self.counter_richieste -= 1
        except:
            print("Vi è stato un errore")


if __name__ == "__main__":
    client = client()
    client.avvio_client()