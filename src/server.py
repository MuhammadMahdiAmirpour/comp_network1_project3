import socket
import struct
from crc import CRC
from hamming_checker import HammingChecker

class Server:
    def __init__(self, host='127.0.0.1', port=65432, window_size=4):
        self.host = host
        self.port = port
        self.server_socket = None
        self.window_size = window_size
        self.expected_seq_num = 0
        self.buffer = {}
        self.received_data = b''
        self.crc = CRC()
        self.crc_key = '1101'  # CRC key
        self.hamming_checker = HammingChecker(3)  # for (7,4) Hamming code

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
        seq_num, payload = struct.unpack(f'!I{len(data)-4}s', data)
        seq_num = seq_num % (self.window_size * 2)  # Wrap around sequence number
        
        print(f"Received packet {seq_num}")

        # Convert payload to binary string
        binary_payload = ''.join(format(byte, '08b') for byte in payload)
        print(f"Received data: {binary_payload[:20]}..., length: {len(binary_payload)}")

        # Check CRC first
        crc_check = self.crc.receiverSide(self.crc_key, binary_payload)

        if crc_check:
            # Check and correct Hamming code
            corrected_payload = ''
            for i in range(0, len(binary_payload), 7):  # for (7,4) Hamming code
                chunk = binary_payload[i:i+7].zfill(7)  # Ensure 7 bits, pad with zeros if needed
                corrected_chunk = self.hamming_checker.correct(chunk)
                corrected_payload += corrected_chunk

            # Extract original data (remove Hamming parity bits)
            original_data = ''
            for i in range(0, len(corrected_payload), 7):
                chunk = corrected_payload[i:i+7]
                original_data += chunk[2] + chunk[4] + chunk[5] + chunk[6]

            # Convert back to bytes
            payload = int(original_data, 2).to_bytes((len(original_data) + 7) // 8, byteorder='big')

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
        else:
            print(f"CRC check failed for packet {seq_num}")
            # Send NACK for packets that fail CRC check
            self.send_nack(seq_num, addr)

    def process_expected_packet(self, seq_num, payload):
        print(f"Processing packet {seq_num}")
        self.received_data += payload
        self.expected_seq_num = (self.expected_seq_num + 1) % (self.window_size * 2)

    def send_ack(self, ack_num, addr):
        if self.server_socket:
            ack = struct.pack('!II', ack_num, 0)  # Use 0 as ACK flag
            try:
                self.server_socket.sendto(ack, addr)
                print(f"Sent ACK {ack_num}")
            except socket.error as e:
                print(f"Error sending ACK: {e}")

    def send_nack(self, nack_num, addr):
        if self.server_socket:
            nack = struct.pack('!II', nack_num, 0xFFFFFFFF)  # Use 0xFFFFFFFF as NACK flag
            try:
                self.server_socket.sendto(nack, addr)
                print(f"Sent NACK {nack_num}")
            except socket.error as e:
                print(f"Error sending NACK: {e}")

    def stop(self):
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        print("Server stopped.")
        print(f"Total data received: {len(self.received_data)} bytes")
        print(f"Received data: {self.received_data[:100]}...")  # Print first 100 bytes of received data

if __name__ == "__main__":
    server = Server()
    server.start()

