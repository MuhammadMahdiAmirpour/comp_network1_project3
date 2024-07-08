import random
import socket
import threading
import numpy as np
from src.frame import Frame
from time import sleep
from crc import generate_invalid_crc

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 65432

WINDOW_SIZE = 4
MAX_SEQ = 8
EOL = b'\0'

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
        self.buffer = b''

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
        self.send_valid_data()
        self.send_valid_data()
        self.send_valid_data()
        self.send_data_with_one_bit_error()
        self.send_valid_data()
        self.send_valid_data()
        self.send_valid_data()
        self.send_data_with_one_bit_error()

    def send_data_with_one_bit_error(self):
        random_bits = generate_random_bits()
        f = Frame(random_bits, seq=self.get_seq_and_increment(), crc=generate_invalid_crc('000' + random_bits))
        self.send_data(f)

    def send_valid_data(self):
        random_bits = generate_random_bits()
        # todo hamming encoding
        f = Frame(random_bits, seq=self.get_seq_and_increment())
        self.send_data(f)

    def send_data(self, f: Frame):
        while self.queue_is_full():
            print('Waiting: Maximum packets sent (window size limit)')
            sleep(1)
        if random.random() < 0.1:  # 10% chance of packet loss
            print(f"Packet loss simulated for sequence number {f.seq}")
            self.decrement_seq()
            return
        self.add_to_queue(f)
        print(f'Sending {f.data}\t{f.seq}\t{f.to_string()}')
        self.connection.sendall(f.to_string().encode() + b'\0')
        sleep(0.25)

    def get_seq_and_increment(self):
        output = self.seq
        self.seq += 1
        self.seq %= MAX_SEQ
        return output

    def receive_acks_or_rejs_thread(self):
        while True:
            self.wait_if_queue_is_empty()
            data = self.connection.recv(1024)
            self.buffer += data
            while EOL in self.buffer:
                seq, self.buffer = self.buffer.split(EOL, 1)
                seq = seq.decode()
                if int(seq) < 0:
                    print(f'ERROR: no synchronization, received_seq: {seq}')
                    self.retransmit_queue()
                else:
                    print(f'receiver: ack\t{seq}')
                    self.pop_from_queue()

    def empty_queue(self):
        queue_lock.acquire()
        self.queue = []
        queue_lock.release()

    def wait_if_queue_is_empty(self):
        while self.queue_is_empty():
            print('Waiting: no un-acknowledged frame remaining')
            sleep(1)

    def pop_from_queue(self):
        queue_lock.acquire()
        f = self.queue.pop(0)
        queue_lock.release()
        return f

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

    def add_to_queue(self, f: Frame):
        queue_lock.acquire()
        self.queue.append(f)
        queue_lock.release()


    def try_transmitting(self):
        try:
            print(f"Connecting to receiver at {DEFAULT_HOST}:{DEFAULT_PORT}")
            transmitter.connect()

            send_to_receiver_thread = threading.Thread(target=self.send_to_receiver_thread)
            receive_acks_thread = threading.Thread(target=self.receive_acks_or_rejs_thread)

            send_to_receiver_thread.start()
            receive_acks_thread.start()

            send_to_receiver_thread.join()
            receive_acks_thread.join()
        except KeyboardInterrupt:
            print("\nClient stopped.")

    def decrement_seq(self):
        if self.seq == 0:
            self.seq = MAX_SEQ
        self.seq -= 1

    def retransmit_queue(self):
        queue_lock.acquire()
        print(f'retransmitting frames with seqs: {[f.seq for f in self.queue]}')
        for f in self.queue:
            f.crc = None
            print(f'Sending {f.data}\t{f.seq}\t{f.to_string()}')
            self.connection.sendall(f.to_string().encode() + b'\0')
        queue_lock.release()

    def get_head_of_queue(self):
        queue_lock.acquire()
        head = self.queue[0]
        queue_lock.release()
        return head


def generate_random_bits():
    return ''.join(map(str, np.random.randint(0, 2, 16)))


if __name__ == "__main__":
    transmitter = Transmitter(DEFAULT_HOST, DEFAULT_PORT)
    transmitter.try_transmitting()
