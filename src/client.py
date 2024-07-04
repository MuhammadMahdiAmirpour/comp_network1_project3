import socket
import threading

class Client:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.client_socket = None
        self.running = False

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.running = True
            print(f"Connected to server at {self.host}:{self.port}")

            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()

            self.send_messages()
        except socket.error as e:
            print(f"Error connecting to server: {e}")
        finally:
            self.disconnect()

    def receive_messages(self):
        while self.running and self.client_socket:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                print(f"Received: {data}")
            except socket.error as e:
                if self.running:
                    print(f"Error receiving message: {e}")
                break
        self.disconnect()

    def send_messages(self):
        while self.running and self.client_socket:
            try:
                message = input()
                if message.lower() == 'quit':
                    break
                if self.client_socket:
                    self.client_socket.send(message.encode('utf-8'))
                else:
                    print("Error: Not connected to server")
                    break
            except socket.error as e:
                print(f"Error sending message: {e}")
                break
        self.disconnect()

    def disconnect(self):
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except socket.error as e:
                print(f"Error closing socket: {e}")
            finally:
                self.client_socket = None
        print("Disconnected from server.")

