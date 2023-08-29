import socket

localIP = "127.0.0.1"  # L'indirizzo IP di questo server
localPORT = 5005  # La porta su cui il server ascolterà

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
