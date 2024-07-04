class CRC:
    def __init__(self):
        self.cdw = ''

    def xor(self, a, b):
        result = []
        for i in range(1, len(b)):
            if a[i] == b[i]:
                result.append('0')
            else:
                result.append('1')
        return ''.join(result)

    def crc(self, message, key):
        pick = len(key)
        tmp = message[:pick]
        while pick < len(message):
            if tmp[0] == '1':
                tmp = self.xor(key, tmp) + message[pick]
            else:
                tmp = self.xor('0' * pick, tmp) + message[pick]
            pick += 1
        if tmp[0] == "1":
            tmp = self.xor(key, tmp)
        else:
            tmp = self.xor('0' * pick, tmp)
        return tmp

    def encodedData(self, data, key):
        try:
            l_key = len(key)
            append_data = data + '0' * (l_key - 1)
            remainder = self.crc(append_data, key)
            codeword = data + remainder
            self.cdw = codeword
            return codeword
        except Exception as e:
            print(f"Error in encodedData: {e}")
            print(f"Input data: {data[:20]}... (length: {len(data)})")
            print(f"Key: {key}")
            return None

    def receiverSide(self, key, data):
        r = self.crc(data, key)
        return all(bit == '0' for bit in r)

if __name__ == "__main__":
    data = '100100'
    key = '1101'
    c = CRC()
    c.encodedData(data, key)
    print('---------------')
    if c.receiverSide(key, c.cdw):
        print("No Error")
    else:
        print("Error")
    print('---------------')
    print(c.cdw)

