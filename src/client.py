import socket
import struct
import time
import threading
import random

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
            packet = struct.pack('!I{}s'.format(len(data)), seq_num, data)
            try:
                # Simulate packet loss
                if random.random() < 0.1:  # 10% chance of packet loss
                    print(f"Packet loss simulated for sequence number {seq_num}")
                    return
                self.client_socket.sendto(packet, (self.host, self.port))
                self.buffer[seq_num] = data
                print(f"Sent packet {seq_num}")
            except socket.error as e:
                print(f"Error sending packet {seq_num}: {e}")

    def receive_acks(self):
        while self.running and self.client_socket:
            try:
                ack, _ = self.client_socket.recvfrom(4)
                ack_num = struct.unpack('!I', ack)[0]
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
                    print(f"Error receiving ACK: {e}")
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
                if i % (self.window_size * 2) in self.buffer:
                    self.send_packet(i % (self.window_size * 2), self.buffer[i % (self.window_size * 2)])
            self.start_timer()

if __name__ == "__main__":
    client = Client()
    data = b"Hello, this is a test message for Go-Back-N protocol." * 100  # Repeat the message to create larger data
    client.send_data(data)

