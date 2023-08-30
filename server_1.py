import socket
import psutil

localIP = "127.0.0.1"  # L'indirizzo IP di questo server
localPORT = 5003  # La porta su cui il server ascolterà

TCPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
TCPServerSocket.bind((localIP, localPORT))
TCPServerSocket.listen()

print('Server UP ({},{}), waiting for connections ...'.format(localIP, localPORT))

while True:
    conn, addr = TCPServerSocket.accept()
    print('Connected by: {}'.format(addr))

    while True:
        data = conn.recv(1024)
        if not data:
            break
        print('{}: received message: {}'.format(addr, data.decode('utf-8')))

        # Esempio di elaborazione del messaggio e invio di una risposta al load balancer
        response = "Risposta dal server di destinazione"
        conn.sendall(response.encode('utf-8'))


        # Qui puoi inserire la logica di elaborazione dei messaggi
        # E inviare una risposta al client se necessario

    conn.close()

 # def crea_comando_random(num_comandi):
 #     """
 #     Funzione che crea richieste/comandi, di carico e durata random.
 #     Ad esempio, possiamo creare comandi random di calcolo; il comando scelto randomicamente verrà quindi
 #     inviato al loadBalancer, che a sua volta lo inoltrerà ad un server

 #     Returns: comando
 #     -------
 #     """
 #     # selezione dei valori di carico e durata random
 #     carico = random.randint(1, 50)
 #     durata = random.randint(1, 50)
 #     # creo due valori random A e B che servono per i calcoli
 #     A = random.randint(1, 50)
 #     B = random.randint(1, 50)
 #     # creo un dizionario di possibili richieste
 #     richieste = {
 #         "somma": A + B,
 #         "sottrazione": A - B,
 #         "moltiplicazione": A * B,
 #         "divisione": A / B}
 #     # seleziono un comando in maniera casuale fra quelli presenti nel dizionario
 #     comando_casuale = random.choice(list(richieste.keys()))
 #     # creo il dizionario comando: ad ogni richiesta, associo un valore di carico e di durata, oltre che la richiesta
 #     # scelta in maniera randomica
 #     comando = {
 #         "carico": carico,
 #         "durata": durata,
 #         "richiesta": comando_casuale}
 #     print(comando)
 #     return comando