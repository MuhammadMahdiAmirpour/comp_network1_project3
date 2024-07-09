import numpy as np

def calculate_2d_parity(data, block_size=8):
    """
    Calculate 2D parity for the given data.
    
    Args:
    data (bytes): Binary data as bytes.
    block_size (int): Size of each block (row length in bits).
    
    Returns:
    tuple: (row_parity, column_parity)
    """
    # Convert bytes to a bit array
    bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
    
    # Reshape the bit array into a 2D grid
    grid = bits[:len(bits) - (len(bits) % block_size)].reshape(-1, block_size)
    
    # Calculate row parity (even parity)
    row_parity = np.sum(grid, axis=1) % 2
    
    # Calculate column parity (even parity)
    column_parity = np.sum(grid, axis=0) % 2
    
    return row_parity, column_parity

def check_2d_parity(received_data, received_row_parity, received_column_parity, block_size=8):
    """
    Check if the received data matches the received 2D parity.
    
    Args:
    received_data (bytes): The binary data received as bytes.
    received_row_parity (numpy.ndarray): The row parity bits received.
    received_column_parity (numpy.ndarray): The column parity bits received.
    block_size (int): Size of each block (row length in bits).
    
    Returns:
    bool: True if the calculated parity matches the received parity, False otherwise.
    """
    calculated_row_parity, calculated_column_parity = calculate_2d_parity(received_data, block_size)
    
    rows_match = np.array_equal(calculated_row_parity, received_row_parity)
    columns_match = np.array_equal(calculated_column_parity, received_column_parity)
    
    if rows_match and columns_match:
        print("2D Parity check successful. Data integrity likely maintained.")
        return True
    else:
        print("2D Parity check failed. Data may be corrupted.")
        if not rows_match:
            print("Row parity mismatch detected.")
        if not columns_match:
            print("Column parity mismatch detected.")
        return False

# Example usage
def string_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')

if __name__ == "__main__":
    # Generate sample data
    data = "10110010" * 1000  # 8000 bits
    block_size = 8

    # Simulate transmission
    original_data = string_to_bytes(data)
    original_row_parity, original_column_parity = calculate_2d_parity(original_data, block_size)

    # In a real scenario, data and parity would be transmitted and could be altered
    received_data = original_data
    received_row_parity = original_row_parity
    received_column_parity = original_column_parity

    # Check received data
    is_data_valid = check_2d_parity(received_data, received_row_parity, received_column_parity, block_size)

    if is_data_valid:
        print("Receiver: Data is likely valid.")
    else:
        print("Receiver: Data may be corrupted.")

    # Simulate an error
    corrupted_data = bytearray(received_data)
    corrupted_data[50] ^= 0x01  # Flip a bit
    is_data_valid = check_2d_parity(corrupted_data, received_row_parity, received_column_parity, block_size)

    if is_data_valid:
        print("Receiver: Data is likely valid.")
    else:
        print("Receiver: Data may be corrupted.")
