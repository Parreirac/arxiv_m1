"""Random variable generators."""
import random
import string


def get_random_string(length):
    """From https://pynative.com/python-generate-random-string/ """
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    #print('Random string of length', length, "is:", result_str)
    return result_str
