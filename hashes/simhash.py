# -*- coding: utf-8 -*-

"""
Implementation of Charikar similarity hashes in Python.

Most useful for creating 'fingerprints' of documents or metadata
so you can quickly find duplicates or cluster items.

Part of python-hashes by sangelone. See README and LICENSE.
"""
from collections import defaultdict

from .hashtype import Hashtype

DEF_HASHBITS = 64


class Simhash(Hashtype):
    def __init__(self, data, hashbits=DEF_HASHBITS):
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


# http://leons.im/posts/a-python-implementation-of-simhash-algorithm/
class SimhashIndex(object):
    def __init__(self, simhashes, bits=2, num_blocks=None):
        self.simhashes = simhashes
        self.hashbits = simhashes[0].hashbits
        self.bits = bits
        self.num_blocks = num_blocks or bits + 1
        max_blocks = self.hashbits // 2

        if self.num_blocks > max_blocks:
            raise ValueError('Number of blocks must not exceed %i' % max_blocks)

        self.block_range = range(self.num_blocks)
        self.bucket = defaultdict(set)
        [self.add(simhash) for simhash in simhashes]

    def add(self, simhash):
        assert simhash.hashbits == self.hashbits

        for key in self.get_keys(simhash):
            self.bucket[key].add(simhash)

    @property
    def offsets(self):
        # http://www.wwwconference.org/www2007/papers/paper215.pdf
        return [self.hashbits // self.num_blocks * i for i in self.block_range]

    def get_keys(self, simhash):
        for i, offset in enumerate(self.offsets):
            if i == len(self.offsets) - 1:
                m = 2 ** (self.hashbits - offset) - 1
            else:
                m = 2 ** (self.offsets[i + 1] - offset) - 1

            c = simhash.hash >> offset & m
            yield '%x:%x' % (c, i)

    def find_dupes(self, simhash):
        for key in self.get_keys(simhash):
            for simhash in self.bucket[key]:
                if simhash.hamming_distance(simhash) <= self.bits:
                    yield simhash
