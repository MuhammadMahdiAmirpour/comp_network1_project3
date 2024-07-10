from utils import str_to_arr, arr_to_str

import numpy as np

class HammingChecker(object):
    """Reads a codeword and checks if the word bits and the parity bits match up"""

    def __init__(self, r):
        """Constructs a Hamming parity-checker"""
        self.r = r
        self.n = 2 ** self.r - 1
        self.checkmatrix = self.__make_checkmatrix()


    def __make_checkmatrix(self):
        """Creates the parity-check matrix for the Hamming code"""
        p_set = set([2 ** i - 1 for i in range(self.r)])
        d_set = set(range(self.n)) - p_set

        checkmatrix = np.zeros((self.n, self.r), dtype=np.uint) # n x r

        # filling in parity bit rows of the parity check matrix
        for d_item in d_set:
            for index in range(self.r):
                checkmatrix[d_item, index] = int(((d_item + 1) >> index) & 1)
     
        # filling in data bit rows of the parity check matrix
        for p_index, p_item in enumerate(p_set):
            checkmatrix[p_item][p_index] = 1  
        
        return checkmatrix


    def get_matching_row(self, row):
        """Searches for a row in the parity-check matrix and returns its index.
           Returns -1 if not found."""
        try:
            return np.where(np.all(self.checkmatrix == row, axis=1))[0][0]
        except IndexError:
            return -1


    def check(self, codeword):
        """Checks if a codeword's word bits and parity bits match up."""
        if len(codeword) != (self.n):
            raise ValueError("Codeword is the wrong length.")

        return self.get_matching_row(np.dot(str_to_arr(codeword), self.checkmatrix) % 2)


    def correct(self, codeword):
        """Tries to correct the corrupted bit."""
        if len(codeword) != (self.n):
            raise ValueError("Codeword is the wrong length.")

        cw_arr = str_to_arr(codeword)
        res = self.get_matching_row(np.dot(cw_arr, self.checkmatrix) % 2)
        
        if res != -1:
            cw_arr[res] = (cw_arr[res] + 1) % 2
            return arr_to_str(cw_arr)
        else:
            return codeword

    def decode(self, codeword):
        corrected_codeword = self.correct(codeword)

        p_set = set([2 ** i - 1 for i in range(self.r)])
        data_bits = [corrected_codeword[i] for i in range(self.n) if i not in p_set]

        return ''.join(data_bits)