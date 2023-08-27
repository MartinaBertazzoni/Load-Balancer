import threading
import socket

alias = input("scegli un nome >> ")
client = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
#client.connect(("192.168.178.103", 5001))  # Indirizzo IP e porta del load balancer
client.connect(("127.0.0.1", 5001))  # Indirizzo IP e porta del load balancer
def client_receive():
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if message == "alias?":
                client.send(alias.encode("utf-8"))
            else:
                print(message)
        except:
            print("vi è stato un errore")
            client.close()
            break


def client_send():
    while True:
        #message = f"{alias}: {input('')}"
        message = input(">>")
        client.send(message.encode("utf-8"))



receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

send_thread = threading.Thread(target=client_send)
send_thread.start()


