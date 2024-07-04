import random
import re
import numpy as np

def str_to_arr(s):
    """Converts binary string to numpy array"""
    if not re.fullmatch(r'(0|1)*', s):
        raise ValueError('Input must be in binary.')
    return np.array([int(d) for d in s], dtype=np.uint)


def arr_to_str(arr):
    """Converts numpy array to string"""
    return re.sub(r'\[|\]|\s+', '', np.array_str(arr))


# ---- Helper functions --- #

def random_word(len):
    """Returns random binary word at the given length"""
    return ''.join([random.choice(('0', '1')) for _ in range(len)])


def add_noise(s, p):
    """Adds noise to transmissions"""
    arr = str_to_arr(s)
    count = 0
    for i in range(len(arr)):
        r = random.random()
        if (r < p):
            arr[i] = (arr[i] + 1) % 2
            count += 1
    return arr_to_str(arr), count
