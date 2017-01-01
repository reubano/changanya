# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
Base class from which hash types can be created.

Part of changanya by reubano. See README and LICENSE.
"""
from functools import total_ordering

DEF_HASHBITS = 96


@total_ordering
class Hashtype(object):
    def __init__(self, hashbits=DEF_HASHBITS):
        self.hashbits = hashbits
        self.hash = None

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        if not hasattr(other, 'hash'):
            return NotImplemented

        return self.hash == other.hash

    def __lt__(self, other):
        if not hasattr(other, 'hash'):
            return NotImplemented

        return self.hash < other.hash

    def __str__(self):
        return str(self.hash)

    def __int__(self):
        return int(self.hash)

    def __float__(self):
        return float(self.hash)

    def hex(self):
        return hex(int(self.hash))

    def hamming_distance(self, other):
        x = (self.hash ^ other.hash) & ((1 << self.hashbits) - 1)
        tot = 0

        while x:
            tot += 1
            x &= x - 1

        return tot

    def similarity(self, other_hash):
        """Calculate how similar this hash is from another hash.
        Returns a float from 0.0 to 1.0 (linear distribution, inclusive)
        """
        if type(other_hash) != self.hashtype:
            raise TypeError('Hashes must be of same type to find similarity')

        if self.hashbits != other_hash.hashbits:
            raise ValueError('Hashes must be of equal size to find similarity')

        numerator = self.hashbits - self.hamming_distance(other_hash)
        return numerator / self.hashbits
