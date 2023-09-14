import socket
import sys
from PIL import Image, ImageDraw
import random
import sys
import pickle
import os


class Client(object):

    def __init__(self):
        self.image_dict={}
        self.contatore_immagini=1


    def avvio_client_socket(self):
        loadBalancer_ip = "127.0.0.1"
        loadBalancer_port = "5006"
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(("127.0.0.1", 60003))
            print(f"Connessione al server {loadBalancer_ip}:{loadBalancer_port} stabilita.")
            return client_socket
        except:
            print(f"Errore durante la connessione al server: {socket.error}")
            sys.exit(1)

    def interfaccia_utente(self):
        while True:
            # richiede il comando da terminale
            comando = input(" Digita il comando:  ")
            if comando == 'exit':
                print("Chiusura della connessione con il server...")
                break
            if comando == 'crea immagine':
                num_richieste = int(input(" Inserisci il numero di immagini da creare:  "))
                for numero in range(num_richieste):
                    image = self.crea_immagine()
                    self.contatore_immagini += 1
                    self.image_list.append(image)
                print(self.image_list)
            else:
                self.interfaccia_utente()

    def crea_immagine(self):
        # Dimensioni dell'immagine
        width = random.randint(1, 50)
        height = random.randint(1, 50)
        # Crea un nuovo oggetto immagine con uno sfondo bianco
        img = Image.new('RGB', (width, height), color='white')
        # Crea un oggetto disegno per modificare l'immagine
        draw = ImageDraw.Draw(img)
        # Genera pixel casuali sull'immagine
        for x in range(width):
            for y in range(height):
                # Genera un colore RGB casuale
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                color = (r, g, b)
                # Disegna un pixel con il colore casuale
                draw.point((x, y), fill=color)
        nome_immagine = f"immagine_{self.contatore_immagini}.png"
        # Salva l'immagine
        img.save(nome_immagine)
        # Visualizza l'immagine (richiede un visualizzatore di immagini esterno)
        img.show()

        file = open(f"immagine_{self.contatore_immagini}.png", "rb")
        file_size=os.path.getsize(f"immagine_{self.contatore_immagini}.png")





    def invia_dati_al_loadbalancer(self, client_socket):
        try:
            while True:
                if len(self.image_dict) != 0:
                    image = self.image_list[0]
                    self.image_list.pop(0)
                    # Serializza l'immagine utilizzando Pickle
                    img_bytes = image.tobytes()
                    # Invia l'immagine serializzata
                    client_socket.sendall(img_bytes)
                    # Chiudi il socket del client
                    client_socket.close()
        except:
            print("Impossibile inviare i dati al load balancer")

    def ricevi_dati_dal_loadbalancer(self):
        pass






if __name__ == "__main__":
    client = Client()
    client_socket = client.avvio_client_socket()
    client.interfaccia_utente()
    client.invia_dati_al_loadbalancer(client_socket)


