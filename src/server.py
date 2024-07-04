import socket
import struct
import random

class Server:
    def __init__(self, host='127.0.0.1', port=65432, window_size=4):
        self.host = host
        self.port = port
        self.server_socket = None
        self.window_size = window_size
        self.expected_seq_num = 0
        self.buffer = {}
        self.received_data = b''

    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.bind((self.host, self.port))
            print(f"Server listening on {self.host}:{self.port}")

            while True:
                try:
                    data, addr = self.server_socket.recvfrom(1024)
                    self.process_packet(data, addr)
                except KeyboardInterrupt:
                    print("\nServer stopped.")
                    break
        except socket.error as e:
            print(f"Socket error: {e}")
        finally:
            self.stop()

    def process_packet(self, data, addr):
        seq_num, payload = struct.unpack('!I{}s'.format(len(data) - 4), data)
        seq_num = seq_num % (self.window_size * 2)  # Wrap around sequence number
        
        # Simulate packet loss
        if random.random() < 0.1:  # 10% chance of packet loss
            print(f"Packet loss simulated for sequence number {seq_num}")
            return

        print(f"Received packet {seq_num}")

        if seq_num == self.expected_seq_num:
            self.process_expected_packet(seq_num, payload)
            
            # Process any buffered packets
            while self.expected_seq_num in self.buffer:
                buffered_payload = self.buffer.pop(self.expected_seq_num)
                self.process_expected_packet(self.expected_seq_num, buffered_payload)
        elif (seq_num > self.expected_seq_num and seq_num < self.expected_seq_num + self.window_size) or \
             (self.expected_seq_num + self.window_size > self.window_size * 2 and seq_num < (self.expected_seq_num + self.window_size) % (self.window_size * 2)):
            # Buffer out-of-order packet
            self.buffer[seq_num] = payload
            print(f"Buffered out-of-order packet {seq_num}")
        
        # Send ACK for the last in-order packet received
        self.send_ack((self.expected_seq_num - 1) % (self.window_size * 2), addr)

    def process_expected_packet(self, seq_num, payload):
        print(f"Processing packet {seq_num}")
        self.received_data += payload
        self.expected_seq_num = (self.expected_seq_num + 1) % (self.window_size * 2)

    def send_ack(self, ack_num, addr):
        if self.server_socket:
            ack = struct.pack('!I', ack_num)
            try:
                self.server_socket.sendto(ack, addr)
                print(f"Sent ACK {ack_num}")
            except socket.error as e:
                print(f"Error sending ACK: {e}")

    def stop(self):
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        print("Server stopped.")
        print(f"Total data received: {len(self.received_data)} bytes")
        print(f"Received data: {self.received_data[:100]}...") # Print first 100 bytes of received data

if __name__ == "__main__":
    server = Server()
    server.start()

