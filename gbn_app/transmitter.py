import random
import queue
import socket
import threading
import numpy as np
from gbn_app.frame import Frame
from time import sleep
from gbn_app.crc import generate_invalid_crc, check_crc
from gbn_app.hamming_encoder import HammingEncoder
import gbn_app.checksum
import gbn_app.parity
from gbn_app.constants import *




queue_lock = threading.Lock()
timers_lock = threading.Lock()

TIMEOUT = 5  # Timeout in seconds

class Transmitter:
    def __init__(self, receiver_host='127.0.0.1', receiver_port=65432):
        self.receiver_host = receiver_host
        self.receiver_port = receiver_port
        self.connection = None
        self.lock = threading.Lock()
        self.timers = {}
        self.ack_received = threading.Event()
        self.seq = 0
        self.queue = []
        self.log_queue = queue.Queue()
        self.buffer = b''
        self.hamming_encoder = HammingEncoder(5)
        self.running = False
    
    def log(self, message):
        print(f"Transmitter: {message}")
        self.log_queue.put(f"Transmitter: {message}")
    
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
                self.log("Transmitter started")
            else:
                self.log("Transmitter already running")
    
    def stop(self):
        with self.lock:
            if self.running:
                self.running = False
                if self.connection:
                    try:
                        self.connection.shutdown(socket.SHUT_RDWR)
                        self.connection.close()
                    except Exception as e:
                        self.log(f"Error closing transmitter connection: {e}")
                if self.thread:
                    self.thread.join(timeout=0)
                if self.timers:
                    for seq in self.timers:
                        self.timers[seq].cancel()
                self.log("Transmitter stopped")
            else:
                self.log("Transmitter already stopped")

    def run(self):
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((self.receiver_host, self.receiver_port))
            self.log(f"Connected to receiver at {self.receiver_host}:{self.receiver_port}")
            self.send_to_receiver_thread()
        except Exception as e:
            self.log(f"Error in transmitter: {e}")
        finally:
            if self.connection:
                self.connection.close()
                self.connection = None
            self.log("Transmitter run completed")

    def connect(self):
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((self.receiver_host, self.receiver_port))
            self.log(f"Client ready to send data to {self.receiver_host}:{self.receiver_port}")
        except socket.error as e:
            self.log(f"Error creating socket: {e}")
            self.log("Failed to create socket. Cannot send data.")
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
        self.send_valid_data()
        self.send_valid_data()
        self.send_valid_data()
        self.send_data_with_one_bit_error()
        self.send_valid_data()
        self.send_valid_data()
        self.send_valid_data()
        self.send_valid_data()
        self.send_valid_data()
        self.send_valid_data()
        self.send_valid_data()
        self.send_valid_data()
        self.send_valid_data()
        self.send_valid_data()
        self.send_valid_data()
        self.send_valid_data()

    def start_timer(self, seq):
        timers_lock.acquire()
        if seq in self.timers:
            self.timers[seq].cancel()
        timer = threading.Timer(TIMEOUT, self.handle_timeout, [seq])
        self.timers[seq] = timer
        self.log(f'starting timer for seq: {seq}')
        timer.start()
        timers_lock.release()

    def handle_timeout(self, seq):
        self.log(f"Timeout occurred for sequence number {seq}")
        self.retransmit_queue()

    def send_data_with_one_bit_error(self):
        random_bits = generate_random_bits()
        seq = self.get_seq_and_increment()
        self.log(f'Invalid CRC with seq {seq}')
        f = Frame(random_bits, seq=seq, crc=generate_invalid_crc('000' + random_bits))
        self.send_data(f)

    def send_valid_data(self):
        random_bits = generate_random_bits()
        f = Frame(random_bits, seq=self.get_seq_and_increment())
        self.send_data(f)

    def send_data(self, f: Frame):
        while self.queue_is_full():
            self.log('Waiting: Maximum packets sent (window size limit)')
            sleep(1)
        if check_crc(f.to_string()):
            frame_is_fucked = self.try_fuck_with_data(f)
            if frame_is_fucked:
                return

        self.send_frame(f, True)
        sleep(0.25)

    def try_fuck_with_data(self, f: Frame):
        rand_value = random.random()
        if rand_value < 0.1:
            self.log(f"Packet loss simulated for seq: {f.seq}, frame: {f.to_string()}")
            self.decrement_seq()
            return True
        if 0.1 < rand_value < 0.2 and ENCODING == Encoding.HAMMING:
            self.log(f'Corrupted hamming code simulated for seq: {f.seq}, frame: {f.to_string()}')
            self.send_corrupted_hamming_code(f)
            return True
        if 0.1 < rand_value < 0.2 and ENCODING == Encoding.PARITY:
            self.log(f'Corrupted parity simulated for seq: {f.seq}, frame: {f.to_string()}')
            self.send_corrupted_parity(f)
            return True

    def send_corrupted_hamming_code(self, f):
        enc = self.encode(f.to_string())
        enc = enc[0:9] + ('0' if enc[9] == '1' else '1') + enc[10:]
        self.add_to_queue(f)
        self.start_timer(f.seq)
        print(f'Sending data: {f.data}\tseq:{f.seq}\tframe:{enc}\tqueue:{self.get_queue_seqs()}'
              f'\ttimers:{self.get_timers_seq()}')
        self.log(f'Sending data: {f.data}\tseq:{f.seq}\tframe:{enc}\tqueue:{self.get_queue_seqs()}')
        self.log(f'\ttimers:{self.get_timers_seq()}')
        self.connection.sendall(enc.encode() + b'\0')

    def send_frame(self, f, encode: bool):
        self.add_to_queue(f)
        self.start_timer(f.seq)
        enc = f.to_string() if encode is False else self.encode(f.to_string())
        self.log(f'Sending data: {f.data}\tseq:{f.seq}\tframe:{enc}\tqueue:{self.get_queue_seqs()}')
        self.log(f'\ttimers:{self.get_timers_seq()}')
        self.connection.sendall(enc.encode() + b'\0')

    def get_seq_and_increment(self):
        output = self.seq
        self.seq += 1
        self.seq %= MAX_SEQ
        return output
 
    def get_logs(self):
        logs = []
        while not self.log_queue.empty():
            try:
                logs.append(self.log_queue.get_nowait())
            except queue.Empty:
                break
        return logs

    def receive_acks_or_rejs_thread(self):
        while True:
            self.wait_if_queue_is_empty()
            data = self.connection.recv(1024)
            self.buffer += data
            while EOL in self.buffer:
                seq, self.buffer = self.buffer.split(EOL, 1)
                seq = seq.decode()
                seq = int(seq)
                if seq < 0:
                    self.log(f'ERROR: no synchronization')
                    self.retransmit_queue()
                else:
                    self.log(f'receiver: ack\t{seq}')
                    self.pop_from_queue()
                    self.stop_timer(seq)

    def empty_queue(self):
        queue_lock.acquire()
        self.queue = []
        queue_lock.release()

    def wait_if_queue_is_empty(self):
        while self.queue_is_empty():
            self.log('Waiting: no un-acknowledged frame remaining')
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
            self.log(f"Connecting to receiver at {DEFAULT_HOST}:{DEFAULT_PORT}")
            transmitter.connect()

            send_to_receiver_thread = threading.Thread(target=self.send_to_receiver_thread)
            receive_acks_thread = threading.Thread(target=self.receive_acks_or_rejs_thread)

            send_to_receiver_thread.start()
            receive_acks_thread.start()

            send_to_receiver_thread.join()
            receive_acks_thread.join()
        except KeyboardInterrupt:
            self.log("\nClient stopped.")

    def decrement_seq(self):
        if self.seq == 0:
            self.seq = MAX_SEQ
        self.seq -= 1

    def retransmit_queue(self):
        queue_lock.acquire()
        self.log(f'retransmitting frames with seqs: {[f.seq for f in self.queue]}')
        for f in self.queue:
            f.crc = None
            enc = self.encode(f.to_string())
            print(f'Sending {f.data}\t{f.seq}\t{enc}')
            self.connection.sendall(enc.encode() + b'\0')
            self.start_timer(f.seq)
        queue_lock.release()

    def get_queue_seqs(self):
        queue_lock.acquire()
        seqs = [f.seq for f in self.queue]
        queue_lock.release()
        return seqs

    def stop_timer(self, seq:int):
        timers_lock.acquire()
        if seq in self.timers.keys():
            self.timers[seq].cancel()
            self.timers.pop(seq)
        else:
            self.log(f'no timers to stop. seq: {seq}\ttimers:{[timer for timer in self.timers]}')
        timers_lock.release()

    def get_timers_seq(self):
        timers_lock.acquire()
        seqs = [timer for timer in self.timers]
        timers_lock.release()
        return seqs

    def send_corrupted_parity(self, f):
        enc = self.encode(f.to_string())
        parity = f.to_string()[-1]
        enc = enc + ('1' if parity == '0' else '1')
        self.add_to_queue(f)
        self.start_timer(f.seq)
        self.log(f'Sending data: {f.data}\tseq:{f.seq}\tframe:{enc}\tqueue:{self.get_queue_seqs()}')
        self.log(f'\ttimers:{self.get_timers_seq()}')
        self.connection.sendall(enc.encode() + b'\0')

    def encode(self, data: str):
        match ENCODING:
            case Encoding.PARITY:
                return data + gbn_app.parity.encode(data)
            case Encoding.TWO_D_PARITY:
                return gbn_app.parity.encode_2d(data)
            case Encoding.CHECKSUM:
                return data + gbn_app.checksum.find_checksum(data)
            case Encoding.HAMMING:
                return self.hamming_encoder.encode(data)


def generate_random_bits():
    return ''.join(map(str, np.random.randint(0, 2, 15)))


if __name__ == "__main__":
    transmitter = Transmitter(DEFAULT_HOST, DEFAULT_PORT)
    transmitter.try_transmitting()
 

