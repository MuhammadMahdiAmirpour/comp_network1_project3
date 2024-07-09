import numpy as np
from .utils import arr_to_str, str_to_arr

# ---- Hamming code classes --- #

# This code assumes that words and codewords are encoded as row vectors.
# Thus, word w is encoded into codeword c with w.G and c is decoded with c.H.

# ---- Hamming encoder class --- #

class HammingEncoder(object):
    """Takes a source message and adds Hamming parity-check bits"""

    def __init__(self, r):
        """Constructs a Hamming encoder"""
        self.r = r
        self.n = 2 ** self.r - 1
        self.genmatrix = self.__make_genmatrix()

        
    def __make_genmatrix(self):
        """Creates the generator matrix for the Hamming code"""
        genmatrix = np.zeros((self.n - self.r, self.n), dtype=np.uint) # k x n

        p_set = set([2 ** i - 1 for i in range(self.r)])
        d_set = set(range(self.n)) - p_set

        # fills in parity bit columns of the generator matrix
        for p_item in p_set:
            for d_index, d_item in enumerate(d_set):
                if (p_item + 1) & (d_item + 1) != 0:
                    genmatrix[d_index][p_item] = 1

        # fills in data bit columns of the generator matrix
        for d_index, d_item in enumerate(d_set):
            genmatrix[d_index][d_item] = 1

        return genmatrix


    def encode(self, word):
        """Constructs a codeword with parity bits given a word of an appropriate length.
           Assumes that the input is a string of 0s and 1s"""
        if len(word) != (self.n - self.r):
            raise ValueError("Wrong word length")

        return arr_to_str(np.dot(str_to_arr(word), self.genmatrix) % 2)

