import queue
import threading
import random
import socket
from gbn_app.hamming_checker import HammingChecker
import gbn_app.frame
from time import sleep
import gbn_app.checksum
import gbn_app.parity
from gbn_app.constants import *


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
        self.log_queue = queue.Queue()
        self.running = False
    
    def log(self, message):
        print(f"Receiver: {message}")
        self.log_queue.put(f"Receiver: {message}")
    
    def get_logs(self):
        logs = []
        while not self.log_queue.empty():
            try:
                logs.append(self.log_queue.get_nowait())
            except queue.Empty:
                break
        return logs

    def clear_logs(self):
        while not self.log_queue.empty():
            try:
                self.log_queue.get_nowait()
            except queue.Empty:
                break
    
    def start(self):
        with self.lock:
            if not self.running:
                self.running = True
                self.thread = threading.Thread(target=self.run)
                self.thread.start()
                self.log("Receiver started")
            else:
                self.log("Receiver already running")

    def stop(self):
        with self.lock:
            if self.running:
                self.running = False
                if self.socket:
                    self.socket.close()
                if self.thread:
                    self.thread.join(timeout=2)
                self.log("Receiver stopped")
            else:
                self.log("Receiver already stopped")

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.log(f"Listening on {self.host}:{self.port}")

        while self.running:
            try:
                self.connection, address = self.socket.accept()
                self.log(f"Connected to {address}")
                self.handle_connection()
            except Exception as e:
                if self.running:
                    self.log(f"Error in receiver: {e}")
            finally:
                if self.connection:
                    self.connection.close()
                    self.connection = None

    def start(self):
        self.receiver_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.allow_address_reuse()
        self.receiver_sock.bind((self.host, self.port))
        self.receiver_sock.listen(1)
        self.log(f"Server listening on {self.host}:{self.port}")

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
                    self.log(f'NACK: f is None')
                    self.send_rej()
                elif f.seq != self.seq:
                    self.log(f'NACK: {f.data}\t{f.seq}')
                else:
                    if random.random() < 0.05:
                        self.log(f'Delaying ACK: {f.data}\t{f.seq}')
                        sleep(5.5)
                    else:
                        self.log(f'ACK: {f.data}\t{f.seq}')
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
        f = gbn_app.frame.build(data)
        if f is None:
            return
        return f

    def decode(self, data: str):
        match ENCODING:
            case Encoding.PARITY:
                return data[:-1]
            case Encoding.TWO_D_PARITY:
                return gbn_app.parity.decode_2d(data)
            case Encoding.CHECKSUM:
                return gbn_app.checksum.find_checksum(data[0:18])
            case Encoding.HAMMING:
                return self.hamming_checker.decode(data)

    def check_valid(self, data: str):
        match ENCODING:
            case Encoding.PARITY:
                parity_bit = data[-1]
                data = data[:-1]
                if gbn_app.parity.encode(data) == parity_bit:
                    return True
                self.log('Invalid Parity')
                return False
            case Encoding.TWO_D_PARITY:
                return gbn_app.parity.check_2d(data)
            case Encoding.CHECKSUM:
                return gbn_app.checksum.find_checksum(data[0:18]) == data[18:]
            case Encoding.HAMMING:
                corrupted_index = self.hamming_checker.check(data)
                if corrupted_index == -1:
                    return True
                self.log(f'Warning: frame is corrupted at index {corrupted_index}')
                self.log(f'Corrected frame is {self.decode(data)}')
                return True


if __name__ == "__main__":
    server = Receiver()
    try:
        server.start()
    except KeyboardInterrupt:
        print("Server stopped")
