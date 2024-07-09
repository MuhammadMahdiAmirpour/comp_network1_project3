def calculate_parity_bit(data, even_parity=True):
    """
    Calculate the parity bit for the given data efficiently.
    
    Args:
    data (bytes): Binary data as bytes.
    even_parity (bool): If True, use even parity; if False, use odd parity.
    
    Returns:
    bool: The parity bit (True for 1, False for 0).
    """
    ones_count = bin(int.from_bytes(data, byteorder='big')).count('1')
    if even_parity:
        return ones_count % 2 == 0
    else:
        return ones_count % 2 != 0

def check_parity(received_data, received_parity_bit, even_parity=True):
    """
    Check if the received data matches the received parity bit.
    
    Args:
    received_data (bytes): The binary data received as bytes.
    received_parity_bit (bool): The parity bit received with the data (True for 1, False for 0).
    even_parity (bool): If True, use even parity; if False, use odd parity.
    
    Returns:
    bool: True if the calculated parity matches the received parity bit, False otherwise.
    """
    calculated_parity = calculate_parity_bit(received_data, even_parity)
    
    if calculated_parity == received_parity_bit:
        print("Parity check successful. Data integrity likely maintained.")
        return True
    else:
        print("Parity check failed. Data may be corrupted.")
        return False


if __name__ == "__main__":
    # Example usage
    def string_to_bytes(s):
        return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')

    # Generate a large amount of data for testing
    large_data = "1011" * 1000000  # 4 million bits
    received_data = string_to_bytes(large_data)
    received_parity_bit = True  # This should be the parity bit sent by the transmitter
    use_even_parity = True
    is_data_valid = check_parity(received_data, received_parity_bit, use_even_parity)
    if is_data_valid:
        print("Receiver: Data is likely valid.")
    else:
        print("Receiver: Data may be corrupted.")

