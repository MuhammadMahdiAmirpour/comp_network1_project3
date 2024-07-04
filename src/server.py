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
        self.buffer = b''

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
        
        # Simulate packet loss
        if random.random() < 0.1:  # 10% chance of packet loss
            print(f"Packet loss simulated for sequence number {seq_num}")
            return

        if seq_num == self.expected_seq_num:
            self.buffer += payload
            self.expected_seq_num += 1
            print(f"Received packet {seq_num}")

            # Send ACK
            self.send_ack(self.expected_seq_num - 1, addr)

            # Process any consecutive packets in buffer
            while self.expected_seq_num in self.buffer:
                self.buffer = self.buffer[len(payload):]
                self.expected_seq_num += 1
        else:
            print(f"Received out-of-order packet {seq_num}, expected {self.expected_seq_num}")
            # Send ACK for the last correctly received packet
            self.send_ack(self.expected_seq_num - 1, addr)

    def send_ack(self, ack_num, addr):
        if self.server_socket:
            ack = struct.pack('!I', ack_num)
            try:
                self.server_socket.sendto(ack, addr)
            except socket.error as e:
                print(f"Error sending ACK: {e}")

    def stop(self):
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        print("Server stopped.")


