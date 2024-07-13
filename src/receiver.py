import random
import socket
from src.encodings.hamming_checker import HammingChecker
import frame
from time import sleep
from src.encodings import parity, checksum
from constants import *


class Receiver:
    def __init__(self, window_size=4):
        self.host = '127.0.0.1'
        self.port = 65432
        self.receiver_sock = None
        self.connection = None
        self.window_size = window_size
        self.seq = 0
        self.buffer = b''
        self.received_data = b''
        self.hamming_checker = HammingChecker(5)

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
            self.buffer += data
            while EOL in self.buffer:
                f, self.buffer = self.buffer.split(EOL, 1)
                f = self.process_data(f.decode())
                if f is None:
                    print(f'NACK: f is None')
                    self.send_rej()
                elif f.seq != self.seq:
                    print(f'NACK: {f.data}\t{f.seq}')
                else:
                    if random.random() < 0.05:
                        print(f'Delaying ACK: {f.data}\t{f.seq}')
                        sleep(5.5)
                    else:
                        print(f'ACK: {f.data}\t{f.seq}')
                    self.send_ack()
            sleep(2)

    def send_ack(self):

        self.send(self.get_seq_and_increment())

    def send(self, input):
        self.connection.sendall(str(input).encode() + EOL)

    def send_rej(self):
        self.send(-1)

    def get_seq_and_increment(self):
        output = self.seq
        self.seq += 1
        self.seq %= MAX_SEQ
        return output

    def allow_address_reuse(self):
        self.receiver_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def process_data(self, data):
        if data == "":
            return
        if self.check_valid(data) is False:
            return
        data = self.decode(data)
        f = frame.build(data)
        if f is None:
            return
        return f

    def decode(self, data: str):
        match ENCODING:
            case Encoding.PARITY:
                return data[:-1]
            case Encoding.TWO_D_PARITY:
                return parity.decode_2d(data)
            case Encoding.CHECKSUM:
                return checksum.find_checksum(data[0:18])
            case Encoding.HAMMING:
                return self.hamming_checker.decode(data)

    def check_valid(self, data: str):
        match ENCODING:
            case Encoding.PARITY:
                parity_bit = data[-1]
                data = data[:-1]
                if parity.encode(data) == parity_bit:
                    return True
                print('Invalid Parity')
                return False
            case Encoding.TWO_D_PARITY:
                return parity.check_2d(data)
            case Encoding.CHECKSUM:
                return checksum.find_checksum(data[0:18]) == data[18:]
            case Encoding.HAMMING:
                corrupted_index = self.hamming_checker.check(data)
                if corrupted_index == -1:
                    return True
                print(f'Warning: frame is corrupted at index {corrupted_index}')
                print(f'Corrected frame is {self.decode(data)}')
                return True


if __name__ == "__main__":
    server = Receiver()
    try:
        server.start()
    except KeyboardInterrupt:
        print("Server stopped")
