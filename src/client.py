import socket
import struct
import threading
import random
from crc import CRC
from hamming_encoder import HammingEncoder

class Client:
    def __init__(self, host='127.0.0.1', port=65432, window_size=4):
        self.host = host
        self.port = port
        self.client_socket = None
        self.window_size = window_size
        self.base = 0
        self.next_seq_num = 0
        self.buffer = {}
        self.lock = threading.Lock()
        self.timer = None
        self.running = False
        self.ack_received = threading.Event()
        self.crc = CRC()
        self.crc_key = '1101'  # CRC key
        self.hamming_encoder = HammingEncoder(3)  # for (7,4) Hamming code

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"Client ready to send data to {self.host}:{self.port}")
        except socket.error as e:
            print(f"Error creating socket: {e}")
            self.client_socket = None

    def send_data(self, data):
        self.connect()
        if not self.client_socket:
            print("Failed to create socket. Cannot send data.")
            return

        self.running = True
        chunks = [data[i:i+1020] for i in range(0, len(data), 1020)]
        
        ack_thread = threading.Thread(target=self.receive_acks)
        ack_thread.start()

        try:
            while self.base < len(chunks):
                with self.lock:
                    while self.next_seq_num < self.base + self.window_size and self.next_seq_num < len(chunks):
                        self.send_packet(self.next_seq_num % (self.window_size * 2), chunks[self.next_seq_num])
                        if self.base == self.next_seq_num:
                            self.start_timer()
                        self.next_seq_num += 1

                self.ack_received.wait(timeout=1.0)
                if not self.ack_received.is_set():
                    self.timeout()
                self.ack_received.clear()

            print("All data sent and acknowledged")
        except Exception as e:
            print(f"Error during data transmission: {e}")
        finally:
            self.running = False
            self.stop_timer()
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None

    def send_packet(self, seq_num, data):
        if self.client_socket:
            # Simulate packet loss
            if random.random() < 0.1:  # 10% chance of packet loss
                print(f"Packet loss simulated for sequence number {seq_num}")
                return

            # Convert data to binary string
            binary_data = ''.join(format(byte, '08b') for byte in data)

            # Apply Hamming encoding
            encoded_data = ''
            for i in range(0, len(binary_data), 4):  # for (7,4) Hamming code
                chunk = binary_data[i:i+4].zfill(4)  # Ensure 4 bits, pad with zeros if needed
                encoded_chunk = self.hamming_encoder.encode(chunk)
                encoded_data += encoded_chunk

            # Apply CRC
            crc_encoded_data = self.crc.encodedData(encoded_data, self.crc_key)
            
            if crc_encoded_data is None:
                print(f"CRC encoding failed for sequence number {seq_num}")
                return

            # Simulate content error (bit flip)
            if random.random() < 0.1:  # 10% chance of content error
                error_pos = random.randint(0, len(crc_encoded_data) - 1)
                crc_encoded_data = crc_encoded_data[:error_pos] + ('1' if crc_encoded_data[error_pos] == '0' else '0') + crc_encoded_data[error_pos + 1:]
                print(f"Content error simulated for sequence number {seq_num}")

            # Convert encoded data back to bytes
            encoded_bytes = int(crc_encoded_data, 2).to_bytes((len(crc_encoded_data) + 7) // 8, byteorder='big')

            packet = struct.pack(f'!I{len(encoded_bytes)}s', seq_num, encoded_bytes)
            try:
                self.client_socket.sendto(packet, (self.host, self.port))
                self.buffer[seq_num] = packet
                print(f"Sent packet {seq_num}, data: {crc_encoded_data[:20]}..., length: {len(crc_encoded_data)}")
            except socket.error as e:
                print(f"Error sending packet {seq_num}: {e}")

    def receive_acks(self):
        while self.running and self.client_socket:
            try:
                ack, _ = self.client_socket.recvfrom(8)
                ack_num, flag = struct.unpack('!II', ack)
                if flag == 0xFFFFFFFF:
                    print(f"Received NACK {ack_num}")
                    with self.lock:
                        self.next_seq_num = ack_num
                        self.start_timer()
                else:
                    with self.lock:
                        if (ack_num >= self.base % (self.window_size * 2)) or \
                           (self.base % (self.window_size * 2) > ack_num and ack_num < (self.base + self.window_size) % (self.window_size * 2)):
                            for i in range(self.base, self.base + self.window_size):
                                if i % (self.window_size * 2) in self.buffer:
                                    del self.buffer[i % (self.window_size * 2)]
                                if i % (self.window_size * 2) == ack_num:
                                    self.base = i + 1
                                    break
                            print(f"Received ACK {ack_num}, base updated to {self.base}")
                            if self.base == self.next_seq_num:
                                self.stop_timer()
                            else:
                                self.start_timer()
                            self.ack_received.set()
            except socket.error as e:
                if self.running:
                    print(f"Error receiving ACK/NACK: {e}")
                break

    def start_timer(self):
        self.stop_timer()
        self.timer = threading.Timer(1.0, self.timeout)
        self.timer.start()

    def stop_timer(self):
        if self.timer:
            self.timer.cancel()

    def timeout(self):
        print("Timeout occurred")
        with self.lock:
            self.next_seq_num = self.base
            for i in range(self.base, min(self.base + self.window_size, self.next_seq_num)):
                if i % (self.window_size * 2) in self.buffer and self.client_socket:
                    try:
                        self.client_socket.sendto(self.buffer[i % (self.window_size * 2)], (self.host, self.port))
                        print(f"Resent packet {i % (self.window_size * 2)}")
                    except socket.error as e:
                        print(f"Error resending packet {i % (self.window_size * 2)}: {e}")
            self.start_timer()

if __name__ == "__main__":
    client = Client()
    data = b"Hello, this is a test message for Go-Back-N protocol." * 100
    client.send_data(data)

