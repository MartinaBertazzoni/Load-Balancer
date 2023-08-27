import sys
import socket
import random


def connessione_al_loadbalancer():
    # impostazione dell'ip del loadBalancer
    loadBalancer_ip = "127.0.0.1"
    # impostazione della porta dove è in ascolto il loadBalancer
    loadBalancer_port = "5001"

    try:
        # creo una socket client
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(client_socket)
        print(loadBalancer_ip)
        # client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # connetto il client con il loadBalancer
        # client_socket.connect((loadBalancer_ip, loadBalancer_port))
        client_socket.connect(("127.0.0.1", 5001))

        print(f"Connessione al server {loadBalancer_ip}:{loadBalancer_port} stabilita.")
        # DEVO RICHIAMARE COME FUNZIONE L'INTERFACCIA_CON_LOADBALANCER()
        interfaccia_con_loadbalancer(client_socket)
        # return client_socket
    except:
        print(f"Errore durante la connessione al server: {socket.error}")
        print("Sto uscendo...")
        sys.exit(1)


def interfaccia_con_loadbalancer(client_socket):
    try:
        while True:
            # ricezione_risposta(client_socket)
            # QUI DOVRO' POI SOSTIUIRE CON COMANDO = CREA_COMANDO_RANDOM()
            comando = input(" Digita il comando:  ")
            # se il comando è ESC, chiudo la connessione con il server
            if comando == 'ESC':
                print("Chiusura della connessione con il server...")
                # chiudo la client socket
                client_socket.close()
                sys.exit(0)
            else:
                # Invia il comando al server (richiamo alla funzione)
                invia_richieste_al_loadbalancer(comando, client_socket)
                ricezione_risposta(client_socket)
    except socket.error as error:
        print(f"Errore di comunicazione con il server: {error}")
        sys.exit(1)


def invia_richieste_al_loadbalancer(comando, client_socket):
    """
    Funzione che invia i comandi al loadBalancer (connessione TCP e socket) e riceve le risposte del loadBalancer

    Returns
    -------
    None.

    """

    # il client invia il comando di input al loadBalancer
    client_socket.send(comando.encode())
    # Riceve la risposta dal server
    # data = client_socket.recv(4096)
    # print(str(data, "utf-8"))
    # if not data:
    #    print("Connessione con il server terminata.")


def crea_comando_random():
    """
    Funzione che crea richieste/comandi, di carico e durata random.
    Ad esempio, possiamo creare comandi random di calcolo; il comando scelto randomicamente verrà quindi
    inviato al loadBalancer, che a sua volta lo inoltrerà ad un server

    Returns: comando
    -------
    """
    # selezione dei valori di carico e durata random
    carico = random.randint(1, 50)
    durata = random.randint(1, 50)
    # creo due valori random A e B che servono per i calcoli
    A = random.randint(1, 50)
    B = random.randint(1, 50)
    # creo un dizionario di possibili richieste
    richieste = {
        "somma": A + B,
        "sottrazione": A - B,
        "moltiplicazione": A * B,
        "divisione": A / B}
    # seleziono un comando in maniera casuale fra quelli presenti nel dizionario
    comando_casuale = random.choice(list(richieste.keys()))
    # creo il dizionario comando: ad ogni richiesta, associo un valore di carico e di durata, oltre che la richiesta
    # scelta in maniera randomica
    comando = {
        "carico": carico,
        "durata": durata,
        "richiesta": comando_casuale}
    print(comando)
    return comando


def ricezione_risposta(client_socket):
    try:
        message = client_socket.recv(1024).decode("utf-8")
        print(message)
    except:
        print("Vi è stato un errore")


if __name__ == "__main__":
    connessione_al_loadbalancer()

