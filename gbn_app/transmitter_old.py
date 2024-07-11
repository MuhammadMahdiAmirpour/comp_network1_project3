# import random
# import socket
# import threading
# import numpy as np
# from .frame import Frame
# from time import sleep
# from .crc import generate_invalid_crc, check_crc

# DEFAULT_HOST = '127.0.0.1'
# DEFAULT_PORT = 65432

# WINDOW_SIZE = 4
# MAX_SEQ = 8
# EOL = b'\0'

# queue_lock = threading.Lock()
# timers_lock = threading.Lock()

# TIMEOUT = 5  # Timeout in seconds


# class Transmitter:
#     def __init__(self, host='127.0.0.1', port=65432):
#         self.host = host
#         self.port = port
#         self.connection = None
#         self.lock = threading.Lock()
#         self.timers = {}
#         self.ack_received = threading.Event()
#         self.seq = 0
#         self.queue = []
#         self.buffer = b''

#     def connect(self):
#         try:
#             self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             self.connection.connect(('127.0.0.1', 65432))
#             print(f"Client ready to send data to {'127.0.0.1'}:{65432}")
#         except socket.error as e:
#             print(f"Error creating socket: {e}")
#             print("Failed to create socket. Cannot send data.")
#             self.connection = None
#             exit()

#     def send_to_receiver_thread(self):
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_data_with_one_bit_error()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_data_with_one_bit_error()

#     def start_timer(self, seq):
#         timers_lock.acquire()
#         if seq in self.timers:
#             self.timers[seq].cancel()
#         timer = threading.Timer(TIMEOUT, self.handle_timeout, [seq])
#         self.timers[seq] = timer
#         print(f'starting timer for seq: {seq}')
#         timer.start()
#         timers_lock.release()

#     def handle_timeout(self, seq):
#         print(f"Timeout occurred for sequence number {seq}")
#         self.retransmit_queue()

#     def send_data_with_one_bit_error(self):
#         random_bits = generate_random_bits()
#         seq = self.get_seq_and_increment()
#         print(f'Invalid CRC with seq {seq}')
#         f = Frame(random_bits, seq=seq, crc=generate_invalid_crc('000' + random_bits))
#         self.send_data(f)

#     def send_valid_data(self):
#         random_bits = generate_random_bits()
#         # todo hamming encoding
#         f = Frame(random_bits, seq=self.get_seq_and_increment())
#         self.send_data(f)

#     def send_data(self, f: Frame):
#         while self.queue_is_full():
#             print('Waiting: Maximum packets sent (window size limit)')
#             sleep(1)
#         if random.random() < 0.1 and check_crc(f.to_string()):  # 10% chance of packet loss only if crc is correct
#             print(f"Packet loss simulated for sequence number {f.seq}")
#             self.decrement_seq()
#             return
#         self.add_to_queue(f)
#         self.start_timer(f.seq)
#         print(f'Sending data: {f.data}\tseq:{f.seq}\tframe:{f.to_string()}\tqueue:{self.get_queue_seqs()}'
#               f'\ttimers:{self.get_timers_seq()}')
#         self.connection.sendall(f.to_string().encode() + b'\0')
#         sleep(0.25)

#     def get_seq_and_increment(self):
#         output = self.seq
#         self.seq += 1
#         self.seq %= MAX_SEQ
#         return output

#     def receive_acks_or_rejs_thread(self):
#         while True:
#             self.wait_if_queue_is_empty()
#             data = self.connection.recv(1024)
#             self.buffer += data
#             while EOL in self.buffer:
#                 seq, self.buffer = self.buffer.split(EOL, 1)
#                 seq = seq.decode()
#                 seq = int(seq)
#                 if seq < 0:
#                     print(f'ERROR: no synchronization, received_seq: {seq}')
#                     self.retransmit_queue()
#                 else:
#                     print(f'receiver: ack\t{seq}')
#                     self.pop_from_queue()
#                     self.stop_timer(seq)

#     def empty_queue(self):
#         queue_lock.acquire()
#         self.queue = []
#         queue_lock.release()

#     def wait_if_queue_is_empty(self):
#         while self.queue_is_empty():
#             print('Waiting: no un-acknowledged frame remaining')
#             sleep(1)

#     def pop_from_queue(self):
#         queue_lock.acquire()
#         f = self.queue.pop(0)
#         queue_lock.release()
#         return f

#     def queue_is_full(self):
#         queue_lock.acquire()
#         queue_length = len(self.queue)
#         queue_lock.release()

#         return queue_length == WINDOW_SIZE

#     def queue_is_empty(self):
#         queue_lock.acquire()
#         l = len(self.queue)
#         queue_lock.release()
#         return l == 0

#     def add_to_queue(self, f: Frame):
#         queue_lock.acquire()
#         self.queue.append(f)
#         queue_lock.release()

#     def try_transmitting(self):
#         try:
#             print(f"Connecting to receiver at {DEFAULT_HOST}:{DEFAULT_PORT}")
#             transmitter.connect()

#             send_to_receiver_thread = threading.Thread(target=self.send_to_receiver_thread)
#             receive_acks_thread = threading.Thread(target=self.receive_acks_or_rejs_thread)

#             send_to_receiver_thread.start()
#             receive_acks_thread.start()

#             send_to_receiver_thread.join()
#             receive_acks_thread.join()
#         except KeyboardInterrupt:
#             print("\nClient stopped.")

#     def decrement_seq(self):
#         if self.seq == 0:
#             self.seq = MAX_SEQ
#         self.seq -= 1

#     def retransmit_queue(self):
#         queue_lock.acquire()
#         print(f'retransmitting frames with seqs: {[f.seq for f in self.queue]}')
#         for f in self.queue:
#             f.crc = None
#             print(f'Sending {f.data}\t{f.seq}\t{f.to_string()}')
#             self.connection.sendall(f.to_string().encode() + b'\0')
#             self.start_timer(f.seq)
#         queue_lock.release()

#     def get_queue_seqs(self):
#         queue_lock.acquire()
#         seqs = [f.seq for f in self.queue]
#         queue_lock.release()
#         return seqs

#     def stop_timer(self, seq:int):
#         timers_lock.acquire()
#         if seq in self.timers.keys():
#             self.timers[seq].cancel()
#             self.timers.pop(seq)
#         else:
#             print(f'no timers to stop. seq: {seq}\ttimers:{[timer for timer in self.timers]}')
#         timers_lock.release()

#     def get_timers_seq(self):
#         timers_lock.acquire()
#         seqs = [timer for timer in self.timers]
#         timers_lock.release()
#         return seqs

# def generate_random_bits():
#     return ''.join(map(str, np.random.randint(0, 2, 16)))


# if __name__ == "__main__":
#     transmitter = Transmitter(DEFAULT_HOST, DEFAULT_PORT)
#     transmitter.try_transmitting()

#### Version 2 ####
# import queue
# import random
# import socket
# import threading
# import numpy as np
# from .frame import Frame
# from time import sleep
# from .crc import generate_invalid_crc, check_crc

# DEFAULT_HOST = '127.0.0.1'
# DEFAULT_PORT = 65432

# WINDOW_SIZE = 4
# MAX_SEQ = 8
# EOL = b'\0'

# queue_lock = threading.Lock()
# timers_lock = threading.Lock()

# TIMEOUT = 5  # Timeout in seconds


# class Transmitter:
#     def __init__(self, receiver_host='localhost', receiver_port=5000, window_size=4, timeout=1.0, max_sequence=8):
#         self.all_data_sent = False
#         # Connection details
#         self.receiver_host = receiver_host
#         self.receiver_port = receiver_port
#         self.connection = None

#         # Go-Back-N protocol parameters
#         self.window_size = window_size
#         self.timeout = timeout
#         self.max_sequence = max_sequence

#         # Sequence number management
#         self.base = 0
#         self.next_seq_num = 0

#         # Threading and running state
#         self.running = False
#         self.thread = None
#         self.lock = threading.Lock()

#         # Queue for logging
#         self.queue = queue.Queue()

#         # Buffer for data to be sent
#         self.data_to_send = [f"Data{i}".encode() for i in range(20)]  # Example data

#         # Window management
#         self.window = {}

#         # Timer management
#         self.timer = None

#         # Statistics
#         self.packets_sent = 0
#         self.packets_acked = 0
#         self.retransmissions = 0

#     def log(self, message):
#         print(f"Transmitter: {message}")
#         self.queue.put(f"Transmitter: {message}")

#     def start(self):
#         with self.lock:
#             if not self.running:
#                 self.running = True
#                 self.thread = threading.Thread(target=self.run)
#                 self.thread.start()
#                 self.log("Transmitter started")
#             else:
#                 self.log("Transmitter already running")

#     def stop(self):
#         with self.lock:
#             if self.running:
#                 self.running = False
#                 if self.connection:
#                     try:
#                         self.connection.shutdown(socket.SHUT_RDWR)
#                         self.connection.close()
#                     except Exception as e:
#                         self.log(f"Error closing transmitter connection: {e}")
#                 if self.thread:
#                     self.thread.join(timeout=2)
#                 if self.timer:
#                     self.timer.cancel()
#                 self.log("Transmitter stopped")
#             else:
#                 self.log("Transmitter already stopped")

#     def run(self):
#         try:
#             self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             self.connection.connect((self.receiver_host, self.receiver_port))
#             self.log(f"Connected to receiver at {self.receiver_host}:{self.receiver_port}")
#             self.send_data()
#         except Exception as e:
#             self.log(f"Error in transmitter: {e}")
#         finally:
#             if self.connection:
#                 self.connection.close()
#                 self.connection = None
#             self.log("Transmitter run completed")
    
#     def connect(self):
#         try:
#             self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             self.connection.connect(('127.0.0.1', 65432))
#             print(f"Client ready to send data to {'127.0.0.1'}:{65432}")
#         except socket.error as e:
#             print(f"Error creating socket: {e}")
#             print("Failed to create socket. Cannot send data.")
#             self.connection = None
#             exit()

#     def send_to_receiver_thread(self):
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_data_with_one_bit_error()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_valid_data()
#         self.send_data_with_one_bit_error()

#     def start_timer(self, seq):
#         timers_lock.acquire()
#         if seq in self.timers:
#             self.timers[seq].cancel()
#         timer = threading.Timer(TIMEOUT, self.handle_timeout, [seq])
#         self.timers[seq] = timer
#         print(f'starting timer for seq: {seq}')
#         timer.start()
#         timers_lock.release()

#     def handle_timeout(self, seq):
#         print(f"Timeout occurred for sequence number {seq}")
#         self.retransmit_queue()

#     def send_data_with_one_bit_error(self):
#         random_bits = generate_random_bits()
#         seq = self.get_seq_and_increment()
#         print(f'Invalid CRC with seq {seq}')
#         f = Frame(random_bits, seq=seq, crc=generate_invalid_crc('000' + random_bits))
#         self.send_data(f)

#     def send_valid_data(self):
#         random_bits = generate_random_bits()
#         # todo hamming encoding
#         f = Frame(random_bits, seq=self.get_seq_and_increment())
#         self.send_data(f)

#     def send_data(self, f: Frame):
#         while self.queue_is_full():
#             print('Waiting: Maximum packets sent (window size limit)')
#             sleep(1)
#         if random.random() < 0.1 and check_crc(f.to_string()):  # 10% chance of packet loss only if crc is correct
#             print(f"Packet loss simulated for sequence number {f.seq}")
#             self.decrement_seq()
#             return
#         self.add_to_queue(f)
#         self.start_timer(f.seq)
#         print(f'Sending data: {f.data}\tseq:{f.seq}\tframe:{f.to_string()}\tqueue:{self.get_queue_seqs()}'
#               f'\ttimers:{self.get_timers_seq()}')
#         self.connection.sendall(f.to_string().encode() + b'\0')
#         sleep(0.25)

#     def get_seq_and_increment(self):
#         output = self.seq
#         self.seq += 1
#         self.seq %= MAX_SEQ
#         return output

#     def receive_acks_or_rejs_thread(self):
#         while True:
#             self.wait_if_queue_is_empty()
#             data = self.connection.recv(1024)
#             self.buffer += data
#             while EOL in self.buffer:
#                 seq, self.buffer = self.buffer.split(EOL, 1)
#                 seq = seq.decode()
#                 seq = int(seq)
#                 if seq < 0:
#                     print(f'ERROR: no synchronization, received_seq: {seq}')
#                     self.retransmit_queue()
#                 else:
#                     print(f'receiver: ack\t{seq}')
#                     self.pop_from_queue()
#                     self.stop_timer(seq)

#     def empty_queue(self):
#         queue_lock.acquire()
#         self.queue = []
#         queue_lock.release()

#     def wait_if_queue_is_empty(self):
#         while self.queue_is_empty():
#             print('Waiting: no un-acknowledged frame remaining')
#             sleep(1)

#     def pop_from_queue(self):
#         queue_lock.acquire()
#         f = self.queue.pop(0)
#         queue_lock.release()
#         return f

#     def queue_is_full(self):
#         queue_lock.acquire()
#         queue_length = len(self.queue)
#         queue_lock.release()

#         return queue_length == WINDOW_SIZE

#     def queue_is_empty(self):
#         queue_lock.acquire()
#         l = len(self.queue)
#         queue_lock.release()
#         return l == 0

#     def add_to_queue(self, f: Frame):
#         queue_lock.acquire()
#         self.queue.append(f)
#         queue_lock.release()

#     def try_transmitting(self):
#         try:
#             print(f"Connecting to receiver at {DEFAULT_HOST}:{DEFAULT_PORT}")
#             self.connect()

#             send_to_receiver_thread = threading.Thread(target=self.send_to_receiver_thread)
#             receive_acks_thread = threading.Thread(target=self.receive_acks_or_rejs_thread)

#             send_to_receiver_thread.start()
#             receive_acks_thread.start()

#             send_to_receiver_thread.join()
#             receive_acks_thread.join()
#         except KeyboardInterrupt:
#             print("\nClient stopped.")

#     def decrement_seq(self):
#         if self.seq == 0:
#             self.seq = MAX_SEQ
#         self.seq -= 1

#     def retransmit_queue(self):
#         queue_lock.acquire()
#         print(f'retransmitting frames with seqs: {[f.seq for f in self.queue]}')
#         for f in self.queue:
#             f.crc = None
#             print(f'Sending {f.data}\t{f.seq}\t{f.to_string()}')
#             self.connection.sendall(f.to_string().encode() + b'\0')
#             self.start_timer(f.seq)
#         queue_lock.release()

#     def get_queue_seqs(self):
#         queue_lock.acquire()
#         seqs = [f.seq for f in self.queue]
#         queue_lock.release()
#         return seqs

#     def stop_timer(self, seq:int):
#         timers_lock.acquire()
#         if seq in self.timers.keys():
#             self.timers[seq].cancel()
#             self.timers.pop(seq)
#         else:
#             print(f'no timers to stop. seq: {seq}\ttimers:{[timer for timer in self.timers]}')
#         timers_lock.release()

#     def get_timers_seq(self):
#         timers_lock.acquire()
#         seqs = [timer for timer in self.timers]
#         timers_lock.release()
#         return seqs

#     def send_data(self):
#         while self.running and self.base < len(self.data_to_send):
#             # Send packets within the window
#             while self.next_seq_num < min(self.base + self.window_size, len(self.data_to_send)):
#                 self.send_packet(self.next_seq_num)
#                 if self.base == self.next_seq_num:
#                     self.start_timer()
#                 self.next_seq_num += 1

#             # Wait for ACK or timeout
#             try:
#                 ack = self.receive_ack()
#                 self.handle_ack(ack)
#             except socket.timeout:
#                 self.handle_timeout()

#         self.log("All data sent successfully")

#     def send_packet(self, seq_num):
#         packet = f"{seq_num}:{self.data_to_send[seq_num].decode()}".encode()
#         self.connection.send(packet)
#         self.window[seq_num] = packet
#         self.log(f"Sent packet {seq_num}")
#         self.packets_sent += 1

#     def receive_ack(self):
#         self.connection.settimeout(self.timeout)
#         ack = int(self.connection.recv(1024).decode())
#         self.connection.settimeout(None)
#         return ack

#     def handle_ack(self, ack):
#         if ack >= self.base:
#             self.log(f"Received ACK {ack}")
#             self.packets_acked += ack - self.base + 1
#             self.base = ack + 1
#             if self.base == self.next_seq_num:
#                 self.stop_timer()
#             else:
#                 self.start_timer()
#             # Remove acknowledged packets from the window
#             self.window = {seq: pkt for seq, pkt in self.window.items() if seq >= self.base}

#     def handle_timeout(self):
#         self.log("Timeout occurred, resending window")
#         self.next_seq_num = self.base
#         self.retransmissions += len(self.window)
#         for seq_num in sorted(self.window.keys()):
#             self.connection.send(self.window[seq_num])
#             self.log(f"Resent packet {seq_num}")
#         self.start_timer()

#     def start_timer(self):
#         if self.timer:
#             self.timer.cancel()
#         self.timer = threading.Timer(self.timeout, self.handle_timeout)
#         self.timer.start()

#     def stop_timer(self):
#         if self.timer:
#             self.timer.cancel()
#             self.timer = None

#     def get_logs(self):
#         logs = []
#         while not self.queue.empty():
#             try:
#                 logs.append(self.queue.get_nowait())
#             except queue.Empty:
#                 break
#         return logs

# def generate_random_bits():
#     return ''.join(map(str, np.random.randint(0, 2, 16)))

#### Versoin 3 ####
import queue
import random
import socket
import threading
import numpy as np
from .frame import Frame
from time import sleep
from .crc import generate_invalid_crc, check_crc

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 65432

WINDOW_SIZE = 4
MAX_SEQ = 8
EOL = b'\0'

queue_lock = threading.Lock()
timers_lock = threading.Lock()

TIMEOUT = 5  # Timeout in seconds

class Transmitter:
    def __init__(self, receiver_host='localhost', receiver_port=5000, window_size=4, timeout=1.0, max_sequence=8):
        # Connection details
        self.receiver_host = receiver_host
        self.receiver_port = receiver_port
        self.connection = None

        # Go-Back-N protocol parameters
        self.window_size = window_size
        self.timeout = timeout
        self.max_sequence = max_sequence

        # Sequence number management
        self.base = 0
        self.next_seq_num = 0
        self.seq = 0

        # Threading and running state
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

        # Queue for logging
        self.queue = queue.Queue()

        # Buffer for data to be sent
        self.data_to_send = [f"Data{i}".encode() for i in range(20)]  # Example data

        # Window management
        self.window = {}

        # Timer management
        self.timer = None
        self.timers = {}

        # Statistics
        self.packets_sent = 0
        self.packets_acked = 0
        self.retransmissions = 0

        # Buffer for received data
        self.buffer = b''

        # Flag for all data sent
        self.all_data_sent = False

    def log(self, message):
        print(f"Transmitter: {message}")
        self.queue.put(f"Transmitter: {message}")

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
                    self.thread.join(timeout=2)
                if self.timer:
                    self.timer.cancel()
                self.log("Transmitter stopped")
            else:
                self.log("Transmitter already stopped")

    def run(self):
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((self.receiver_host, self.receiver_port))
            self.log(f"Connected to receiver at {self.receiver_host}:{self.receiver_port}")
            self.send_data()
        except Exception as e:
            self.log(f"Error in transmitter: {e}")
        finally:
            if self.connection:
                self.connection.close()
                self.connection = None
            self.log("Transmitter run completed")

    def send_data(self):
        while self.running and self.base < len(self.data_to_send):
            # Send packets within the window
            while self.next_seq_num < min(self.base + self.window_size, len(self.data_to_send)):
                self.send_packet(self.next_seq_num)
                if self.base == self.next_seq_num:
                    self.start_timer()
                self.next_seq_num += 1

            # Wait for ACK or timeout
            try:
                ack = self.receive_ack()
                self.handle_ack(ack)
            except socket.timeout:
                self.handle_timeout()

        self.all_data_sent = True
        self.log("All data sent successfully")

    def send_packet(self, seq_num):
        packet = f"{seq_num}:{self.data_to_send[seq_num].decode()}".encode()
        self.connection.send(packet + EOL)
        self.window[seq_num] = packet
        self.log(f"Sent packet {seq_num}")
        self.packets_sent += 1

    def receive_ack(self):
        self.connection.settimeout(self.timeout)
        data = self.connection.recv(1024)
        self.connection.settimeout(None)
        ack = int(data.split(EOL)[0].decode())
        return ack

    def handle_ack(self, ack):
        if 0 <= ack < self.max_sequence and ack >= self.base:
            self.log(f"Received ACK {ack}")
            self.packets_acked += ack - self.base + 1
            self.base = (ack + 1) % self.max_sequence
            if self.base == self.next_seq_num:
                self.stop_timer()
            else:
                self.start_timer()
            # Remove acknowledged packets from the window
            self.window = {seq: pkt for seq, pkt in self.window.items() if seq >= self.base}
        else:
            self.log(f"Received invalid ACK {ack}")

    def handle_timeout(self):
        if not self.all_data_sent:
            self.log("Timeout occurred, resending window")
            self.next_seq_num = self.base
            self.retransmissions += len(self.window)
            for seq_num in sorted(self.window.keys()):
                self.send_packet(seq_num)
            self.start_timer()

    def start_timer(self):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(self.timeout, self.handle_timeout)
        self.timer.start()

    def stop_timer(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def get_logs(self):
        logs = []
        while not self.queue.empty():
            try:
                logs.append(self.queue.get_nowait())
            except queue.Empty:
                break
        return logs

def generate_random_bits():
    return ''.join(map(str, np.random.randint(0, 2, 16)))

