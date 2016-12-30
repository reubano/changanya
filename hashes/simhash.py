"""
Implementation of Charikar similarity hashes in Python.

Most useful for creating 'fingerprints' of documents or metadata
so you can quickly find duplicates or cluster items.

Part of python-hashes by sangelone. See README and LICENSE.
"""

from hashtype import Hashtype

class Simhash(Hashtype):
    def __init__(self, tokens, hashbits=96):
        _hash = self.create_hash(tokens)
        super(Simhash, self).__init__(_hash, hashbits=hashbits)

    def create_hash(self, tokens):
        """Calculates a Charikar simhash with appropriate bitlength.

        Input can be any iterable, but for strings it will automatically
        break it into words first, assuming you don't want to iterate
        over the individual characters.

        Reference used: http://dsrg.mff.cuni.cz/~holub/sw/shash
        """
        if type(tokens) == str:
            tokens = tokens.split()

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

    def _string_hash(self, v):
        "A variable-length version of Python's builtin hash. Neat!"
        if v == "":
            return 0
        else:
            x = ord(v[0])<<7
            m = 1000003
            mask = 2**self.hashbits-1
            for c in v:
                x = ((x*m)^ord(c)) & mask
            x ^= len(v)
            if x == -1:
                x = -2
            return x

    def similarity(self, other_hash):
        """Calculate how similar this hash is from another Simhash.
        Returns a float from 0.0 to 1.0 (linear distribution, inclusive)
        """
        if type(other_hash) != self:
            raise TypeError('Hashes must be of same type to find similarity')

        if self.hashbits != other_hash.hashbits:
            raise ValueError('Hashes must be of equal size to find similarity')

        numerator = self.hashbits - self.hamming_distance(other_hash)
        return numerator / self.hashbits
