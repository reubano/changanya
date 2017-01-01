# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
Implementation of Charikar similarity hashes in Python.

Most useful for creating 'fingerprints' of documents or metadata
so you can quickly find duplicates or cluster items.

Part of changanya by reubano. See README and LICENSE.
"""
import itertools as it

from collections import defaultdict
from operator import attrgetter
from functools import reduce

from changanya.hashtype import Hashtype

DEF_HASHBITS = 64


def pairwise(iterable):
    a, b = it.tee(iterable)
    next(b, None)
    return zip(a, b)


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


# https://github.com/seomoz/simhash-cpp/blob/master/src/permutation.cpp
# https://moz.com/devblog/near-duplicate-detection/
class Permuter(object):
    def __init__(self, bits, masks, widths, hashbits=DEF_HASHBITS):
        self.bits = bits
        self.masks = masks
        self.hashbits = hashbits
        self.widths = widths

        width_range = range(len(widths))
        self.offsets = [
            self.hashbits - sum(self.widths[:i + 1]) - 1 for i in width_range]

    @property
    def search_mask(self):
        # Alright, we have to determine the low and high masks for this
        # particular table. If we are searching for up to `bits` differing bits,
        # then we should  include all but the last `bits` blocks in our mask.
        width = sum(self.widths[:-self.bits])

        # Set the first /width/ bits in the low mask to 1, and then shift it up
        # until it's a full bit number.
        _search_mask = reduce(lambda x, y: (x << 1) | 1, range(width), 0)
        reducer = lambda x, y: x << 1
        return reduce(reducer, range(self.hashbits - width), _search_mask)

    def permute(self, _hash):
        def reducer(x, y):
            mask, offset = y

            if offset > 0:
                return x | ((_hash & mask) << offset)
            else:
                return x | ((_hash & mask) >> -offset)

        return reduce(reducer, zip(self.masks[1:], self.offsets), 0)


# http://leons.im/posts/a-python-implementation-of-simhash-algorithm/
class SimhashIndex(object):
    def __init__(self, simhashes, bits=2, num_blocks=6):
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
        first = [self.hashbits // self.num_blocks * i for i in self.block_range]
        return first + [self.hashbits]

    @property
    def widths(self):
        return [j - i for i, j in pairwise(self.offsets)]

    @property
    def bit_widths(self):
        return [2 ** width - 1 for width in self.widths]

    @property
    def blocks(self):
        # https://github.com/seomoz/simhash-cpp/blob/master/src/permutation.cpp#L82
        for i in self.block_range:
            start = (i * self.hashbits) // self.num_blocks
            end = ((i + 1) * self.hashbits) // self.num_blocks
            yield reduce(lambda x, y: x | (1 << y), range(start, end), 0)

    def get_keys(self, simhash):
        for i, pair in enumerate(zip(self.offsets, self.bit_widths)):
            offset, bit_width = pair
            key = simhash.hash >> offset & bit_width
            yield '%x:%x' % (key, i)

    def find_dupes(self, simhash):
        for key in self.get_keys(simhash):
            for simhash in self.bucket[key]:
                if simhash.hamming_distance(simhash) <= self.bits:
                    yield simhash

    # https://github.com/seomoz/simhash-cpp/blob/master/src/simhash.cpp
    def find_all_dupes(self):
        blocks = list(self.blocks)
        widths = self.widths

        for permutation in it.permutations(self.block_range, self.bits):
            extra = set(permutation).symmetric_difference(self.block_range)
            order = permutation + tuple(extra)
            masks = [blocks[i] for i in order]
            new_widths = [widths[i] for i in order]
            permuter = Permuter(
                self.bits, masks, new_widths, hashbits=self.hashbits)

            for simhash in self.simhashes:
                simhash.permhash = permuter.permute(simhash.hash)

            permuted = sorted(self.simhashes, key=attrgetter('permhash'))
            mask = permuter.search_mask
            start = permuted[0]
            end_func = lambda x: (x.permhash & mask) == (start.permhash & mask)

            for i, simhash in enumerate(it.takewhile(end_func, permuted)):
                for other in it.takewhile(end_func, permuted[i + 1:]):
                    if simhash.hamming_distance(other) <= self.bits:
                        pair = [simhash, other]
                        yield tuple(sorted(pair, key=attrgetter('hash')))
