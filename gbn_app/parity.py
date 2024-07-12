import numpy as np



def encode(n: str):
    return str(n.count('1') % 2)



def string_to_2d_array(bitstring, row_length):
    """
    Converts a string of bits to a 2D list.
    """
    return [list(map(int, bitstring[i:i+row_length])) for i in range(0, len(bitstring), row_length)]

def array_to_string(array):
    """
    Converts a 2D list to a string of bits.
    """
    return ''.join(''.join(map(str, row)) for row in array)

def encode_2d(bitstring, row_length=4):
    data = string_to_2d_array(bitstring, row_length)
    rows, cols = len(data), len(data[0])
    encoded = [[0] * (cols + 1) for _ in range(rows + 1)]

    # Copy original data
    for i in range(rows):
        for j in range(cols):
            encoded[i][j] = data[i][j]

    # Calculate row parity
    for i in range(rows):
        encoded[i][-1] = sum(data[i]) % 2

    # Calculate column parity
    for j in range(cols):
        encoded[-1][j] = sum(data[i][j] for i in range(rows)) % 2

    # Calculate overall parity
    encoded[-1][-1] = sum(encoded[i][-1] for i in range(rows)) % 2

    return array_to_string(encoded)

def decode_2d(encoded_bitstring, row_length=4):
    encoded = string_to_2d_array(encoded_bitstring, row_length + 1)
    return array_to_string([row[:-1] for row in encoded[:-1]])

def check_2d(encoded_bitstring, row_length=4):
    encoded = string_to_2d_array(encoded_bitstring, row_length + 1)
    rows, cols = len(encoded) - 1, len(encoded[0]) - 1
    data = [row[:-1] for row in encoded[:-1]]
    row_parity = [row[-1] for row in encoded[:-1]]
    col_parity = encoded[-1][:-1]
    overall_parity = encoded[-1][-1]

    # Check row parity
    for i in range(rows):
        if sum(data[i]) % 2 != row_parity[i]:
            return False

    # Check column parity
    for j in range(cols):
        if sum(data[i][j] for i in range(rows)) % 2 != col_parity[j]:
            return False

    # Check overall parity
    if sum(row_parity) % 2 != overall_parity:
        return False

    return True
