# from struct import pack, unpack
# from math import log2

# def strbin_to_hexbyte(data: str):
#     hex_value = b''
#     while len(data) > 0:
#         current_byte = data[-8:]
#         data = data[:-8]
#         integer_value = strbin_to_int(current_byte)
#         hex_value = pack('!H', integer_value) + hex_value
#     return hex_value


# def int_to_strbin8(data: int):
#     return int_to_strbin(data, 8)

# def int_to_strbin(data: int, power=0):
#     return format(data, f'0{power}b')


# def strbin_to_int(data: str):
#     return int(data, 2)


# def hexbyte_to_strbin8(data: bytes):
#     str_value = ''
#     while len(data) > 0:
#         current_nipple = data[-2:]
#         data = data[:-2]
#         integer_value = unpack('!H', current_nipple)[0]
#         str_value = int_to_strbin8(integer_value) + str_value
#     return str_value


# def hexbyte_to_strbin(data: bytes):
#     return bin(int(data, 16))[2:]

from struct import pack, unpack
from math import log2

def strbin_to_hexbyte(data: str):
    return bytes(int(data[i:i+8], 2) for i in range(0, len(data), 8))

def hexbyte_to_strbin8(data: bytes):
    return ''.join(format(byte, '08b') for byte in data)

def int_to_strbin8(data: int):
    return int_to_strbin(data, 8)

def int_to_strbin(data: int, power=0):
    return format(data, f'0{power}b')

def strbin_to_int(data: str):
    return int(data, 2)

def hexbyte_to_strbin8(data: bytes):
    return ''.join(format(byte, '08b') for byte in data)

