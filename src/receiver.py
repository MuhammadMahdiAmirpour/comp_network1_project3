import socket
from hamming_checker import HammingChecker
import frame
from time import sleep

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 65432
WINDOW_SIZE = 4


class Receiver:
    def __init__(self, window_size=4):
        self.host = '127.0.0.1'
        self.port = 65432
        self.receiver_sock = None
        self.connection = None
        self.window_size = window_size
        self.seq = 0
        self.buffer = {}
        self.received_data = b''
        self.hamming_checker = HammingChecker(3)  # for (7,4) Hamming code

    def start(self):
        self.receiver_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.allow_address_reuse()
        self.receiver_sock.bind((self.host, self.port))
        self.receiver_sock.listen(1)
        print(f"Server listening on {self.host}:{self.port}")

        while True:
            self.connection, client_address = self.receiver_sock.accept()
            self.receive_from_transmitter()

    def receive_from_transmitter(self):
        while True:
            data = self.connection.recv(1024)
            f = self.process_data(data.decode())
            self.send_ack(f.seq)
            sleep(2)


    def send_ack(self, seq:int):
        self.connection.sendall(str(seq).encode())

    def allow_address_reuse(self):
        self.receiver_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def process_data(self, data):
        if data == "":
            return
        f = frame.build(data)
        if f is None:
            return
        print(f'received: {f.data}\t{f.seq}')
        return f


if __name__ == "__main__":
    server = Receiver()
    try:
        server.start()
    except KeyboardInterrupt:
        print("Server stopped")
    finally:
        server.stop()
