# -*- coding: utf-8 -*-

"""
Implementation of Charikar similarity hashes in Python.

Most useful for creating 'fingerprints' of documents or metadata
so you can quickly find duplicates or cluster items.

Part of python-hashes by sangelone. See README and LICENSE.
"""

from .hashtype import Hashtype


class Simhash(Hashtype):
    def __init__(self, data, hashbits=96):
        self.hashtype = Simhash
        super(Simhash, self).__init__(hashbits)
        self.hash = self.create_hash(data)

    def _string_hash(self, v):
        "A variable-length version of Python's builtin hash. Neat!"
        if v == '':
            return 0
        else:
            x = ord(v[0]) << 7
            m = 1000003
            mask = 2 ** self.hashbits - 1

            for c in v:
                x = ((x * m) ^ ord(c)) & mask

            x ^= len(v)

            if x == -1:
                x = -2

            return x

    def create_hash(self, data):
        """Calculates a Charikar simhash with appropriate bitlength.

        Input can be any iterable, but for strings it will automatically
        break it into words first, assuming you don't want to iterate
        over the individual characters.

        Reference used: http://dsrg.mff.cuni.cz/~holub/sw/shash
        """
        tokens = data.split() if type(data) == str else data
        v = [0] * self.hashbits

        for t in [self._string_hash(x) for x in tokens]:
            bitmask = 0

            for i in range(self.hashbits):
                bitmask = 1 << i
                v[i] += 1 if t & bitmask else -1

        _hash = 0

        for i in range(self.hashbits):
            if v[i] >= 0:
                _hash += 1 << i

        return _hash
