"""
basic usage::
    >>> # Here is a quick simhash example
    >>> from hashes.simhash import Simhash
    >>>
    >>> hash1 = Simhash('This is a test string one.')
    >>> hash2 = Simhash('This is a test string TWO.')
    >>> hash1  # doctest: +ELLIPSIS
    <hashes.simhash.Simhash object at 0x...>
    >>> print(hash1)
    10203485745788768176630988232
    >>> print(hash2)
    10749932022170787621889701832
    >>> hash1.hex()
    '0x20f82026a01daffae45cfdc8'
    >>> # % of bits in common (calculated via hamming distance)
    >>> hash1.similarity(hash2)
    0.875
    >>> int(hash1) - int(hash2)
    -546446276382019445258713600
    >>> hash1 < hash2       # Hashes of the same type can be compared
    True
    >>> a_list = [hash2, hash1]
    >>> for item in a_list:
    ...     print(item)
    10749932022170787621889701832
    10203485745788768176630988232
    >>>
    >>> a_list.sort()       # Because comparisons work, so does sorting
    >>> for item in a_list:
    ...     print(item)
    10203485745788768176630988232
    10749932022170787621889701832

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

    >>> # Here is the basic Bloom filter use case
    >>> from hashes.bloom import Bloomfilter
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
    >>> from hashes.geohash import Geohash
    >>>
    >>> here = Geohash(33.0505, -1.024, precision=4)
    >>> there = Geohash(34.5, -2.5, precision=4)
    >>> here.hash, there.hash
    ('evzs', 'eynk')
    >>> here.distance_in_miles(there)
    Decimal('131.2474342505055105445599395')

    >>> # The longer the hash, the more accurate it is
    >>> here.encode(precision=8)
    >>> here.hash
    'evzk08wt'
    >>> here.decode()
    (33.05056571960449, -1.0236167907714844)

    >>> # Now try with 20 characters
    >>> here.encode(precision=20)
    >>> here.hash
    'evzk08wm55drbqbww0j7'
    >>> here.decode()
    (33.050499999999936, -1.023999999999834)
"""
