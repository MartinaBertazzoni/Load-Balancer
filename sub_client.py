# importazione del modulo per lavorare con le socket
import socket
import sys




def invia_comandi(s):
    while True:
        comando = input("->")
        if comando == "ESC":
            print("Sto chiudendo la connessione con il server")
            s.close()
            sys.exit()
        else:
            s.send(comando.encode())
            data = s.recv(4096)
            print(str(data, "utf-8"))


def conn_sub_server(indirizzo_server):
    try:
        s = socket.socket() # creazione socket client
        s.connect(indirizzo_server) # connessione al server
        print(f"Connessione al Server {indirizzo_server} stabilita")
    except socket.error as errore: 
        print(f"Qualcosa è andato storto, sto uscendo... \n{errore}")
        sys.exit()
    invia_comandi(s)

if __name__ == "__main__":
    conn_sub_server(("192.168.64.1", 15000))