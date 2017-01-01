# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
basic usage::
    >>> # Here is a quick simhash example
    >>> from changanya.simhash import Simhash
    >>>
    >>> hash1 = Simhash('This is a test string one.')
    >>> hash2 = Simhash('This is a test string TWO.')
    >>> hash1  # doctest: +ELLIPSIS
    <changanya.simhash.Simhash object at 0x...>
    >>> print(hash1)
    11537571312501063112
    >>> print(hash2)
    11537571196679550920
    >>> hash1.hex()
    '0xa01daffae45cfdc8'
    >>> # % of bits in common (calculated via hamming distance)
    >>> hash1.similarity(hash2)
    0.890625
    >>> int(hash1) - int(hash2)
    115821512192
    >>> hash1 < hash2       # Hashes of the same type can be compared
    False
    >>> a_list = [hash2, hash1]
    >>> for item in a_list:
    ...     print(item)
    11537571196679550920
    11537571312501063112
    >>>
    >>> a_list.sort(reverse=True)  # Because comparisons work, so does sorting
    >>> for item in a_list:
    ...     print(item)
    11537571312501063112
    11537571196679550920

    >>> # It can be extended to any bitlength using the `hashbits` parameter.

    >>> hash3 = Simhash('this is yet another test', hashbits=8)
    >>> hash3.hex()
    '0x18'
    >>> hash4 = Simhash('extremely long hash bitlength', hashbits=2048)
    >>> hash4.hex()
    '0xf00020585012016060260443bab0f7d76fde5549a6857ec'

    >>> # But be careful; it only makes sense to compare equal-length hashes!
    >>> hash3.similarity(hash4)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ValueError: Hashes must be of equal size to find similarity

    >>> # Use the Simhash Index
    >>> from changanya.simhash import SimhashIndex
    >>>
    >>> data = [
    ...     'How are you? I Am fine. blar blar blar blar blar Thanks.',
    ...     'How are you i am fine. blar blar blar blar blar than',
    ...     'This is simhash test.']
    >>> hashes = [Simhash(text) for text in data]
    >>> for simhash in hashes:
    ...     print(simhash)
    1318951168287673739
    1318951168283479435
    13366613251191922586
    >>> index = SimhashIndex(hashes, num_blocks=6)
    >>> len(index.bucket)
    13
    >>> simhash = Simhash('How are you im fine. blar blar blar blar thank')
    >>> dupe = next(index.find_dupes(simhash))
    >>> dupe == hashes[0]
    True
    >>> index.add(simhash)
    >>> simhash.hash
    1318986352659762571
    >>> dupe = next(index.find_dupes(simhash))
    >>> dupe == simhash
    True
    >>> result = next(index.find_all_dupes())
    >>> dupe1, dupe2 = result
    >>> (dupe1, dupe2) == (hashes[1], hashes[0])
    True
    >>> dupe1.similarity(dupe2)
    0.984375
    >>> dupe1.hamming_distance(dupe2)
    1

    >>> # Here is the basic Bloom filter use case
    >>> from changanya.bloom import Bloomfilter
    >>>
    >>> hash1 = Bloomfilter('test')
    >>> hash1.hashbits, hash1.num_hashes     # default values (see below)
    (28756, 7)
    >>> hash1.add('test string')
    >>> 'test string' in hash1
    True
    >>> 'holy diver' in hash1
    False
    >>> for word in 'these are some tokens to add to the filter'.split():
    ...     hash1.add(word)
    >>> 'these' in hash1
    True
    >>> hash2 = Bloomfilter(capacity=100, false_positive_rate=0.01)
    >>> hash2.hashbits, hash2.num_hashes
    (959, 7)
    >>> hash3 = Bloomfilter(capacity=1000000, false_positive_rate=0.01)
    >>> hash3.hashbits, hash3.num_hashes
    (9585059, 7)
    >>> hash4 = Bloomfilter(capacity=1000000, false_positive_rate=0.0001)
    >>> hash4.hashbits, hash4.num_hashes
    (19170117, 14)
    >>> hash1.hex()  # doctest: +ELLIPSIS
    '0x100000000000000004...'
    >>> import zlib
    >>> len(hash1.hex())
    7062
    >>> len(zlib.compress(hash1.hex().encode('utf-8')))
    220

    >>> # Geohash example
    >>> from changanya.geohash import Geohash
    >>>
    >>> here = Geohash('33.050500000000', '-1.024', precision=4)
    >>> there = Geohash('34.5000000000', '-2.500', precision=4)
    >>> here.hash, there.hash
    ('evzs', 'eynk')
    >>> here.decode()
    (Decimal('33.050500'), Decimal('-1.024'))
    >>> here.distance_in_miles(there)
    Decimal('131.24743')

    >>> # The higher the precision, the longer the hash is
    >>> here.encode(precision=8)
    >>> here.hash
    'evzk08wt'
    >>> here.decode()
    (Decimal('33.0505000000'), Decimal('-1.024'))
    >>> # We can also decode arbitrary hashes
    >>> here.decode('evzk08wt')
    (Decimal('33.0504798889'), Decimal('-1.024'))
    >>> here.distance_in_miles(there)
    Decimal('131.247434251')

    >>> # But we can't gain more precision than we started with
    >>> here.encode(precision=16)
    >>> here.precision
    10
    >>> here.max_precision
    10
    >>> here.hash
    'evzk08wm57'
    >>> here.decode()
    (Decimal('33.050500000000'), Decimal('-1.024'))
    >>> there.max_precision
    8
    >>> here.distance_precision
    8
    >>> here.distance_in_miles(there)
    Decimal('131.247434251')
"""
