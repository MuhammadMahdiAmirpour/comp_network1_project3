import unittest
from src.convertor import strbin_to_hexbyte, int_to_strbin8, strbin_to_int, hexbyte_to_strbin8


class TestConvertor(unittest.TestCase):

    def test_strbin_to_hexbyte(self):
        self.assertEqual(b'\x00\x01\x00\x02', strbin_to_hexbyte('0000000100000010'))
        self.assertEqual(b'\x00\x02\x00\x03', strbin_to_hexbyte('0000001000000011'))
        self.assertEqual(b'\xff\x00\x01', strbin_to_hexbyte('1111111100000001'))
        self.assertEqual(b'\x00\x00', strbin_to_hexbyte('00000000'))

    def test_int_to_strbin(self):
        self.assertEqual('00000001', int_to_strbin8(1))
        self.assertEqual('00000010', int_to_strbin8(2))
        self.assertEqual('11111111', int_to_strbin8(255))
        self.assertEqual('00000000', int_to_strbin8(0))

    def test_strbin_to_int(self):
        self.assertEqual(1, strbin_to_int('00000001'))
        self.assertEqual(2, strbin_to_int('00000010'))
        self.assertEqual(255, strbin_to_int('11111111'))
        self.assertEqual(0, strbin_to_int('00000000'))

    def test_hexbyte_to_strbin(self):
        self.assertEqual('0000000100000010', hexbyte_to_strbin8(b'\x00\x01\x00\x02'))
        self.assertEqual('0000001000000011', hexbyte_to_strbin8(b'\x00\x02\x00\x03'))
        self.assertEqual('1111111100000001', hexbyte_to_strbin8(b'\xff\x00\x01'))
        self.assertEqual('00000000', hexbyte_to_strbin8(b'\x00\x00'))


if __name__ == '__main__':
    unittest.main()
