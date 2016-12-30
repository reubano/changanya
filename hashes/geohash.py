# -*- coding: utf-8 -*-

"""
Geohash is a latitude / longitude geocode system invented by
Gustavo Niemeyer when writing the web service at geohash.org, and put
into the public domain.

It is a hierarchical spatial data structure which subdivides space
into buckets of grid shape. Geohashes offer properties like
arbitrary precision and the possibility of gradually removing
characters from the end of the code to reduce its size (and
gradually lose precision). As a consequence of the gradual
precision degradation, nearby places will often (but not always)
present similar prefixes. On the other side, the longer a shared
prefix is, the closer the two places are.

Part of python-hashes by sangelone. See README and LICENSE.
Based on code by Hiroaki Kawai <kawai@iij.ad.jp> and geohash.org
"""

import math
from .hashtype import Hashtype

_BASE32 = '0123456789bcdefghjkmnpqrstuvwxyz'
_BASE32_MAP = {_BASE32[i]: i for i in range(len(_BASE32))}


class Geohash(Hashtype):
    # Not the actual RFC 4648 standard; a variation


    def __init__(self, lat=0, lon=0, precision=12):
        super(Geohash, self).__init__()
        self.encode(lat, lon, precision)

    def _encode_i2c(self, lat, lon, lat_length, lon_length):
        precision = (lat_length + lon_length) // 5
        a, b = lat, lon

        if lat_length < lon_length:
            a, b = lon, lat

        boost = (0, 1, 4, 5, 16, 17, 20, 21)
        ret = ''

        for i in range(precision):
            ret += _BASE32[(boost[a & 7] + (boost[b & 3] << 1)) & 0x1F]
            a, b = b >> 2, a >> 3

        return ret[::-1]

    def encode(self, latitude, longitude, precision):
        self.latitude = latitude
        self.longitude = longitude

        if latitude >= 90 or latitude < -90:
            raise Exception("invalid latitude")

        while longitude < -180:
            longitude += 360

        while longitude >= 180:
            longitude -= 360

        lat = latitude / 180
        lon = longitude / 360

        lat_length = lon_length = precision * 5 // 2
        lon_length += precision & 1

        # Here is where we decide encoding based on quadrant..
        # points near the equator, for example, will have widely
        # differing hashes because of this
        if lat > 0:
            lat = int((1 << lat_length) * lat) + (1 << (lat_length - 1))
        else:
            lat = (1 << lat_length - 1) - int((1 << lat_length) * -lat)

        if lon > 0:
            lon = int((1 << lon_length) * lon) + (1 << (lon_length - 1))
        else:
            lon = (1 << lon_length - 1) - int((1 << lon_length) * -lon)

        self.hash = self._encode_i2c(lat, lon, lat_length, lon_length)

    def _decode_c2i(self, hashcode):
        lon = 0
        lat = 0
        bit_length = 0
        lat_length = 0
        lon_length = 0

        # Unrolled for speed and clarity
        for i in hashcode:
            t = _BASE32_MAP[i]

            if not (bit_length & 1):
                lon = lon << 3
                lat = lat << 2
                lon += (t >> 2) & 4
                lat += (t >> 2) & 2
                lon += (t >> 1) & 2
                lat += (t >> 1) & 1
                lon += t & 1
                lon_length += 3
                lat_length += 2
            else:
                lon = lon << 2
                lat = lat << 3
                lat += (t >> 2) & 4
                lon += (t >> 2) & 2
                lat += (t >> 1) & 2
                lon += (t >> 1) & 1
                lat += t & 1
                lon_length += 2
                lat_length += 3

            bit_length += 5

        return (lat, lon, lat_length, lon_length)

    def decode(self):
        lat, lon, lat_length, lon_length = self._decode_c2i(self.hash)
        lat = (lat << 1) + 1
        lon = (lon << 1) + 1
        lat_length += 1
        lon_length += 1

        latitude = 180 * (lat - (1 << (lat_length - 1))) / (1 << lat_length)
        longitude = 360 * (lon - (1 << (lon_length - 1))) / (1 << lon_length)

        self.latitude = latitude
        self.longitude = longitude
        return (latitude, longitude)

    def __int__(self):
        pass

    def __float__(self):
        pass

    def hex(self):
        pass

    def unit_distance(self, lat1, lon1, lat2, lon2):
        degrees_to_radians = math.pi / 180
        phi1 = (90 - lat1) * degrees_to_radians
        phi2 = (90 - lat2) * degrees_to_radians
        theta1 = lon1 * degrees_to_radians
        theta2 = lon2 * degrees_to_radians

        # Compute spherical distance from spherical coordinates.
        cos = (
            math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2) +
            math.cos(phi1) * math.cos(phi2))

        return math.acos(cos)

    def distance(self, other_hash):
        lat, lon = self.latitude, self.longitude
        other_lat, other_lon = other_hash.latitude, other_hash.longitude
        return self.unit_distance(lat, lon, other_lat, other_lon)

    def distance_in_miles(self, other_hash):
        return self.distance(other_hash) * 3960

    def distance_in_km(self, other_hash):
        return self.distance(other_hash) * 6373
