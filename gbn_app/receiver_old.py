# import random
# import socket
# from .hamming_checker import HammingChecker
# from . import frame
# from time import sleep

# DEFAULT_HOST = '127.0.0.1'
# DEFAULT_PORT = 65432
# WINDOW_SIZE = 4
# EOL = b'\0'
# MAX_SEQ = 8

# class Receiver:
#     def __init__(self, window_size=4):
#         self.host = '127.0.0.1'
#         self.port = 65432
#         self.receiver_sock = None
#         self.connection = None
#         self.window_size = window_size
#         self.seq = 0
#         self.buffer = b''
#         self.received_data = b''
#         self.hamming_checker = HammingChecker(3)  # for (7,4) Hamming code

#     def start(self):
#         self.receiver_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.allow_address_reuse()
#         self.receiver_sock.bind((self.host, self.port))
#         self.receiver_sock.listen(1)
#         print(f"Server listening on {self.host}:{self.port}")

#         while True:
#             self.connection, client_address = self.receiver_sock.accept()
#             self.receive_from_transmitter()

#     def receive_from_transmitter(self):
#         while True:
#             data = self.connection.recv(1024)
#             self.buffer += data
#             while EOL in self.buffer:
#                 f, self.buffer = self.buffer.split(EOL, 1)
#                 f = self.process_data(f.decode())
#                 if f is None:
#                     print(f'NACK: f is None')
#                     self.send_rej()
#                 elif f.seq != self.seq:
#                     print(f'NACK: {f.data}\t{f.seq}')
#                 else:
#                     if random.random() < 0.05:
#                         print(f'Delaying ACK: {f.data}\t{f.seq}')
#                         sleep(5.5)
#                     else:
#                         print(f'ACK: {f.data}\t{f.seq}')
#                     self.send_ack()
#             sleep(2)

#     def send_ack(self):

#         self.send(self.get_seq_and_increment())

#     def send(self, input):
#         self.connection.sendall(str(input).encode() + EOL)

#     def send_rej(self):
#         self.send(-self.seq)

#     def get_seq_and_increment(self):
#         output = self.seq
#         self.seq += 1
#         self.seq %= MAX_SEQ
#         return output

#     def allow_address_reuse(self):
#         self.receiver_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#     def process_data(self, data):
#         if data == "":
#             return
#         f = frame.build(data)
#         if f is None:
#             return
#         return f



# if __name__ == "__main__":
#     server = Receiver()
#     try:
#         server.start()
#     except KeyboardInterrupt:
#         print("Server stopped")

#### Version 2 #####
# import threading
# import queue
# import socket
# from .hamming_checker import HammingChecker
# from . import frame
# from time import sleep

# import random
# import socket
# from hamming_checker import HammingChecker
# import frame
# from time import sleep

# class Receiver:
#     def __init__(self, host='localhost', port=5000, window_size=4, max_sequence=8):
#         # Connection details
#         self.host = host
#         self.port = port
#         self.socket = None
#         self.connection = None

#         # Go-Back-N protocol parameters
#         self.window_size = window_size
#         self.max_sequence = max_sequence

#         # Sequence number management
#         self.expected_seq_num = 0

#         # Threading and running state
#         self.running = False
#         self.thread = None
#         self.lock = threading.Lock()

#         # Queue for logging
#         self.queue = queue.Queue()

#         # Buffer for received data
#         self.received_data = []

#         # Statistics
#         self.packets_received = 0
#         self.packets_accepted = 0
#         self.packets_discarded = 0

#     def log(self, message):
#         print(f"Receiver: {message}")
#         self.queue.put(f"Receiver: {message}")

#     def start(self):
#         with self.lock:
#             if not self.running:
#                 self.running = True
#                 self.thread = threading.Thread(target=self.run)
#                 self.thread.start()
#                 self.log("Receiver started")
#             else:
#                 self.log("Receiver already running")

#     def stop(self):
#         with self.lock:
#             if self.running:
#                 self.running = False
#                 if self.socket:
#                     self.socket.close()
#                 if self.thread:
#                     self.thread.join(timeout=2)
#                 self.log("Receiver stopped")
#             else:
#                 self.log("Receiver already stopped")

#     def run(self):
#         self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         self.socket.bind((self.host, self.port))
#         self.socket.listen(1)
#         self.log(f"Listening on {self.host}:{self.port}")

#         while self.running:
#             try:
#                 self.connection, address = self.socket.accept()
#                 self.log(f"Connected to {address}")
#                 self.handle_connection()
#             except Exception as e:
#                 if self.running:
#                     self.log(f"Error in receiver: {e}")
#             finally:
#                 if self.connection:
#                     self.connection.close()
#                     self.connection = None

#     def handle_connection(self):
#         while self.running:
#             try:
#                 data = self.connection.recv(1024)
#                 if not data:
#                     break
#                 self.process_packet(data)
#             except Exception as e:
#                 self.log(f"Error handling connection: {e}")
#                 break

#     def process_packet(self, packet):
#         try:
#             seq_num, data = packet.decode().split(':', 1)
#             seq_num = int(seq_num)
#             self.packets_received += 1
#             self.log(f"Received packet with sequence number {seq_num}")

#             if seq_num == self.expected_seq_num:
#                 self.received_data.append(data)
#                 self.packets_accepted += 1
#                 self.expected_seq_num = (self.expected_seq_num + 1) % self.max_sequence
#                 self.log(f"Accepted packet {seq_num}, expected next: {self.expected_seq_num}")
#             else:
#                 self.packets_discarded += 1
#                 self.log(f"Discarded packet {seq_num}, expected: {self.expected_seq_num}")

#             self.send_ack(self.expected_seq_num - 1)
#         except Exception as e:
#             self.log(f"Error processing packet: {e}")

#     def send_ack(self, ack_num):
#         try:
#             self.connection.sendall(str(ack_num).encode())
#             self.log(f"Sent ACK {ack_num}")
#         except Exception as e:
#             self.log(f"Error sending ACK: {e}")

#     def get_logs(self):
#         logs = []
#         while not self.queue.empty():
#             try:
#                 logs.append(self.queue.get_nowait())
#             except queue.Empty:
#                 break
#         return logs

#     def get_received_data(self):
#         return ''.join(self.received_data)

#     def get_statistics(self):
#         return {
#             "packets_received": self.packets_received,
#             "packets_accepted": self.packets_accepted,
#             "packets_discarded": self.packets_discarded
#         }

#### Version 3 ####
import socket
import threading
import queue
from .frame import Frame
from .crc import check_crc

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 65432

WINDOW_SIZE = 4
MAX_SEQ = 8
EOL = b'\0'

class Receiver:
    def __init__(self, host='localhost', port=5000, window_size=4, max_sequence=8):
        # Connection details
        self.host = host
        self.port = port
        self.socket = None
        self.connection = None

        # Go-Back-N protocol parameters
        self.window_size = window_size
        self.max_sequence = max_sequence

        # Sequence number management
        self.expected_seq_num = 0

        # Threading and running state
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

        # Queue for logging
        self.queue = queue.Queue()

        # Buffer for received data
        self.received_data = []

        # Statistics
        self.packets_received = 0
        self.packets_accepted = 0
        self.packets_discarded = 0

    def log(self, message):
        print(f"Receiver: {message}")
        self.queue.put(f"Receiver: {message}")

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

    def handle_connection(self):
        buffer = b''
        while self.running:
            try:
                data = self.connection.recv(1024)
                if not data:
                    break
                buffer += data
                while EOL in buffer:
                    packet, buffer = buffer.split(EOL, 1)
                    self.process_packet(packet)
            except Exception as e:
                self.log(f"Error handling connection: {e}")
                break

    def process_packet(self, packet):
        try:
            seq_num, data = packet.decode().split(':', 1)
            seq_num = int(seq_num)
            self.packets_received += 1
            self.log(f"Received packet with sequence number {seq_num}")

            if seq_num == self.expected_seq_num:
                # Check CRC if implemented
                if check_crc(data):
                    self.received_data.append(data)
                    self.packets_accepted += 1
                    self.expected_seq_num = (self.expected_seq_num + 1) % self.max_sequence
                    self.log(f"Accepted packet {seq_num}, expected next: {self.expected_seq_num}")
                else:
                    self.log(f"Discarded packet {seq_num} due to CRC error")
                    self.packets_discarded += 1
            else:
                self.packets_discarded += 1
                self.log(f"Discarded packet {seq_num}, expected: {self.expected_seq_num}")

            # Always send ACK for the last correctly received packet
            self.send_ack((self.expected_seq_num - 1) % self.max_sequence)
        except Exception as e:
            self.log(f"Error processing packet: {e}")

    def send_ack(self, ack_num):
        try:
            self.connection.sendall(str(ack_num).encode() + EOL)
            self.log(f"Sent ACK {ack_num}")
        except Exception as e:
            self.log(f"Error sending ACK: {e}")

    def get_logs(self):
        logs = []
        while not self.queue.empty():
            try:
                logs.append(self.queue.get_nowait())
            except queue.Empty:
                break
        return logs

    def get_received_data(self):
        return ''.join(self.received_data)

    def get_statistics(self):
        return {
            "packets_received": self.packets_received,
            "packets_accepted": self.packets_accepted,
            "packets_discarded": self.packets_discarded
        }

