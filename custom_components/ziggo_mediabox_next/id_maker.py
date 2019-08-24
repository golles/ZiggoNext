import string
import random


class IdMaker(object):
    @staticmethod
    def make(stringLength=10):
        letters = string.ascii_lowercase
        return "".join(random.choice(letters) for i in range(stringLength))
