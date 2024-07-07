import random
import socket
import threading
import numpy as np
from src.frame import Frame
from time import sleep

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 65432

WINDOW_SIZE = 4
MAX_SEQ = 8

queue_lock = threading.Lock()


class Transmitter:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.connection = None
        self.lock = threading.Lock()
        self.timer = None
        self.ack_received = threading.Event()
        self.seq = 0
        self.queue = []

    def connect(self):
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect(('127.0.0.1', 65432))
            print(f"Client ready to send data to {'127.0.0.1'}:{65432}")
        except socket.error as e:
            print(f"Error creating socket: {e}")
            print("Failed to create socket. Cannot send data.")
            self.connection = None
            exit()

    def send_to_receiver_thread(self):
        self.send_valid_data()
        self.send_valid_data()
        self.send_valid_data()
        self.send_valid_data()
        self.send_data_with_one_bit_error()

    def send_data_with_one_bit_error(self):
        random_bits = generate_random_bits()
        f = Frame(random_bits, seq=self.get_seq_and_increment())
        print(f'Sending {random_bits}\t{f.seq}\t{f.to_string()}')
        data = f.to_string()
        bit_error_index = random.randint(0, len(data))
        wrong_bit = '1' if int(data[bit_error_index]) == 0 else '0'
        data = data[0:bit_error_index] + wrong_bit + data[bit_error_index + 1:]
        self.send_data(data)

    def send_valid_data(self):
        random_bits = generate_random_bits()
        # todo hamming encoding
        f = Frame(random_bits, seq=self.get_seq_and_increment())
        print(f'Sending {f.data}\t{f.seq}\t{f.to_string()}')
        self.send_data(f.to_string())

    def send_data(self, data: str):
        while self.queue_is_full():
            sleep(1)
        if random.random() < 0.1:  # 10% chance of packet loss
            print(f"Packet loss simulated for sequence number {self.seq}")
            self.seq -= 1
            return

        self.connection.sendall(data.encode())

    def get_seq_and_increment(self):
        output = self.seq
        self.seq += 1
        self.seq %= MAX_SEQ
        return output

    def receive_acks_thread(self):
        received_seq = self.connection.recv(1024).decode()
        while self.queue_is_empty():
            sleep(0.5)
        queue_lock.acquire()
        expected_seq = self.queue.pop(0)
        queue_lock.release()
        if int(received_seq) != expected_seq:
            print(f'ERROR: no synchronization, received_seq: {received_seq}, expected_seq: {expected_seq}')
            queue_lock.acquire()
            self.queue = []
            queue_lock.release()
            self.seq = expected_seq

    def queue_is_full(self):
        queue_lock.acquire()
        queue_length = len(self.queue)
        queue_lock.release()

        return queue_length == WINDOW_SIZE

    def queue_is_empty(self):
        queue_lock.acquire()
        l = len(self.queue)
        queue_lock.release()

        return l == 0

    def try_transmitting(self):
        try:
            print(f"Connecting to receiver at {DEFAULT_HOST}:{DEFAULT_PORT}")
            transmitter.connect()

            send_to_receiver_thread = threading.Thread(target=self.send_to_receiver_thread)
            receive_acks_thread = threading.Thread(target=self.receive_acks_thread)

            send_to_receiver_thread.start()
            receive_acks_thread.start()

            send_to_receiver_thread.join()
            receive_acks_thread.join()
        except KeyboardInterrupt:
            print("\nClient stopped.")


def generate_random_bits():
    return ''.join(map(str, np.random.randint(0, 2, 16)))


if __name__ == "__main__":
    transmitter = Transmitter(DEFAULT_HOST, DEFAULT_PORT)
    transmitter.try_transmitting()
