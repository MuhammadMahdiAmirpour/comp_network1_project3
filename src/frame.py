import crc
import convertor

MAX_SEQ_BITS = 3
MAX_SEQ = 8


def build(d: str):
    if d == '':
        print('ERROR: no value')
        return
    if not crc.check_crc(d):
        print(f'ERROR: invalid CRC\t{d}')
        return
    data = d[MAX_SEQ_BITS:-len(crc.CRC8_POLYNOMIAL)+1]
    frame = Frame(data)
    frame.seq = convertor.strbin_to_int(d[0:MAX_SEQ_BITS])
    return frame


class Frame:
    def __init__(self, data, seq=None):
        self.seq = seq
        self.data = data

    def to_string(self):
        sending_data = convertor.int_to_strbin(self.seq, MAX_SEQ_BITS) + self.data
        return crc.encode_data(sending_data)
