def find_checksum(message, div=8):
    mess_len = len(message)

    temp = message[:div]
    message = message[div:]
    for i in range((mess_len // div) - 1):
        temp = _binSum(temp, message[:div])
        message = message[div:]

    checkSum = temp
    for i in range(len(checkSum)):
        if checkSum[i] == '0':
            checkSum = checkSum[:i] + '1' + checkSum[i + 1:]
        else:
            checkSum = checkSum[:i] + '0' + checkSum[i + 1:]
    return checkSum


def _binSum(chunk1, chunk2, div=8):
    st = bin(int(chunk1, 2) + int(chunk2, 2))

    if len(st) == div + 3:
        carry = '1'
        st1 = st[3:]
        st = _binSum(st1, carry)
        return st
    else:
        return st[2:]


