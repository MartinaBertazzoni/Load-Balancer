

import socket
import threading

class LoadBalancer:
    def _init_(self, server_ips, server_ports, client_listen_ip, client_listen_port, server_listen_ip, server_listen_port):
        self.server_ips = server_ips
        self.server_ports = server_ports
        self.current_server_index = -1
        self.connected_clients = []
        self.client_listen_ip = client_listen_ip
        self.client_listen_port = client_listen_port
        self.server_listen_ip = server_listen_ip
        self.server_listen_port = server_listen_port

    def handle_client(self, client_socket):
        while True:
            request = client_socket.recv(1024)
            if not request:
                break
            
            # Implementa il bilanciamento del carico round-robin
            next_server = self.get_next_server()
            
            try:
                server_socket = self.get_server_socket_for_client(client_socket, next_server)
                server_socket.sendall(request)
                
                response = server_socket.recv(4096)
                if response:
                    client_socket.sendall(response)
            except Exception as e:
                print(f"Error connecting to server {next_server['ip']}:{next_server['port']}: {e}")
            
        self.remove_client_server_connection(client_socket)
        client_socket.close()

    def handle_server(self, server_socket):
        while True:
            response = server_socket.recv(4096)
            if not response:
                break
            
            try:
                client_socket = self.get_client_socket_for_server(server_socket)
                client_socket.sendall(response)
            except Exception as e:
                print(f"Error sending response to client: {e}")
        
        server_socket.close()

    def get_next_server(self):
        # Implementa la logica per selezionare il prossimo server disponibile
        # Round-robin: cicla tra gli indirizzi IP e le porte dei server
        self.current_server_index = (self.current_server_index + 1) % len(self.server_ips)
        return {"ip": self.server_ips[self.current_server_index], "port": self.server_ports[self.current_server_index], "socket": self.connected_clients[self.current_server_index]["server_socket"]}

    def get_server_socket_for_client(self, client_socket, next_server):
        # Associa il socket del server al socket del client
        # Inserisce la coppia client-server nella lista connected_clients
        self.connected_clients.append({"client_socket": client_socket, "server_socket": next_server["socket"]})
        return next_server["socket"]

    def get_client_socket_for_server(self, server_socket):
        # Trova il client_socket associato al server_socket nella connessione
        # In questo caso, sappiamo che client e server sono sempre connessi in coppia
        # quindi associamo il primo socket client_socket che incontriamo a server_socket
        for connection in self.connected_clients:
            if connection.get("server_socket") == server_socket:
                return connection["client_socket"]

    def remove_client_server_connection(self, client_socket):
        # Rimuove la coppia client-server dalla lista connected_clients
        for connection in self.connected_clients:
            if connection.get("client_socket") == client_socket:
                self.connected_clients.remove(connection)

    def connect_to_servers(self):
        for server_ip, server_port in zip(self.server_ips, self.server_ports):
            try:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.connect((server_ip, server_port))
                self.connected_clients.append({"server_socket": server_socket})
                print(f"Connected to server {server_ip}:{server_port}")
            except Exception as e:
                print(f"Error connecting to server {server_ip}:{server_port}: {e}")

    def start(self):
        # Connettiti ai server reali all'avvio del server-loadBalancer
        self.connect_to_servers()

        client_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_listener.bind((self.client_listen_ip, self.client_listen_port))
        client_listener.listen(5)
        
        server_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_listener.bind((self.server_listen_ip, self.server_listen_port))
        server_listener.listen(5)

        print(f"Load Balancer is listening for clients on {self.client_listen_ip}:{self.client_listen_port}")
        print(f"Load Balancer is listening for servers on {self.server_listen_ip}:{self.server_listen_port}")

        while True:
            client_socket, client_address = client_listener.accept()
            print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
            
            server_socket, server_address = server_listener.accept()
            print(f"Connected to server {server_address[0]}:{server_address[1]}")

            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            server_thread = threading.Thread(target=self.handle_server, args=(server_socket,))
            client_thread.start()
            server_thread.start()

if __name__ == "__main__":
    # Definisci gli indirizzi IP e le porte dei server
    server_ips = ["127.0.0.1", "127.0.0.1"]  # List of server IP addresses
    server_ports = [9000, 9001]  # List of server ports

    # Configurazione del server-loadBalancer
    lb = LoadBalancer(server_ips,server_ports=server_ports,client_listen_ip="127.0.0.1",client_listen_port=7555,server_listen_ip="127.0.0.1",server_listen_port=9090)

    # Avvia il server-loadBalancer
    lb.start()