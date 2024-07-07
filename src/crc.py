import convertor

CRC8_POLYNOMIAL = "100000111"


def __xor(a, b):
    result = []
    for i in range(1, len(b)):
        if a[i] == b[i]:
            result.append('0')
        else:
            result.append('1')
    return ''.join(result)


def __mod2div(dividend, divisor):
    pick = len(divisor)
    tmp = dividend[0:pick]

    while pick < len(dividend):
        if tmp[0] == '1':
            tmp = __xor(divisor, tmp) + dividend[pick]
        else:
            tmp = __xor('0' * pick, tmp) + dividend[pick]
        pick += 1

    if tmp[0] == '1':
        tmp = __xor(divisor, tmp)
    else:
        tmp = __xor('0' * pick, tmp)

    return tmp


def encode_data(data, key=CRC8_POLYNOMIAL):
    l_key = len(key)
    appended_data = data + '0' * (l_key - 1)
    remainder = __mod2div(appended_data, key)
    codeword = data + remainder
    return codeword


def check_crc(data, key=CRC8_POLYNOMIAL):
    remainder = __mod2div(data, key)
    if '1' in remainder:
        return False
    return True


if __name__ == "__main__":
    data = "11010011101100"
    key = "100000111"

    # Encode data
    encoded_data = encode_data(data, key)
    print("Encoded Data (with CRC):", encoded_data)

    # Check if CRC is correct
    if check_crc(encoded_data):
        print("The CRC is correct.")
    else:
        print("The CRC is incorrect.")

    # Example of checking a data with CRC
    check_data = "110100111011001101101"
    if check_crc(check_data):
        print("The given CRC data is correct.")
    else:
        print("The given CRC data is incorrect.")

