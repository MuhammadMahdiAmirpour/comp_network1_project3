import zlib
from functools import reduce

def simple_sum_checksum(binary_string):
    """
    Calculate a simple sum checksum of a binary string.
    """
    return sum(int(bit) for bit in binary_string)

def xor_checksum(binary_string):
    """
    Calculate an XOR checksum of a binary string.
    """
    return reduce(lambda x, y: x ^ y, (int(bit) for bit in binary_string))

def crc32_checksum(binary_string):
    """
    Calculate CRC-32 checksum of a binary string.
    """
    # Convert binary string to bytes
    byte_string = int(binary_string, 2).to_bytes((len(binary_string) + 7) // 8, byteorder='big')
    return zlib.crc32(byte_string)


def check_checksum(received_data, received_checksum):
    """
    Check if the received data matches the received checksum.
    
    Args:
    received_data (str): The binary string data received.
    received_checksum (int): The checksum value received with the data.
    
    Returns:
    bool: True if the calculated checksum matches the received checksum, False otherwise.
    """
    # Convert binary string to bytes
    byte_data = int(received_data, 2).to_bytes((len(received_data) + 7) // 8, byteorder='big')
    
    # Calculate CRC-32 checksum of the received data
    calculated_checksum = zlib.crc32(byte_data)
    
    # Compare calculated checksum with received checksum
    if calculated_checksum == received_checksum:
        print("Checksum verification successful. Data integrity maintained.")
        return True
    else:
        print("Checksum verification failed. Data may be corrupted.")
        return False

if __name__ == "__main__":
    # Example usage
    binary_string = "1011001010110010101100101011001"

    print(f"Binary string: {binary_string}")
    print(f"Simple sum checksum: {simple_sum_checksum(binary_string)}")
    print(f"XOR checksum: {xor_checksum(binary_string)}")
    print(f"CRC-32 checksum: {crc32_checksum(binary_string)}")

    # Example usage
    received_data = "1011001010110010101100101011001"
    received_checksum = 2380432710  # This should be the checksum sent by the transmitter

    is_data_valid = check_checksum(received_data, received_checksum)

    if is_data_valid:
        print("Receiver: Data is valid.")
    else:
        print("Receiver: Data is corrupted.")
