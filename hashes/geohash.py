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

from decimal import Decimal
from .hashtype import Hashtype

_BASE32 = '0123456789bcdefghjkmnpqrstuvwxyz'
_BASE32_MAP = {_BASE32[i]: i for i in range(len(_BASE32))}


class Geohash(Hashtype):
    # Not the actual RFC 4648 standard; a variation
    def __init__(self, latitude=0, longitude=0, precision=12):
        dec_latitude = Decimal(latitude)
        dec_longitude = Decimal(longitude)

        if dec_latitude >= 90 or dec_latitude < -90:
            raise Exception("invalid latitude")

        self.latitude = dec_latitude
        self.longitude = dec_longitude

        while dec_longitude < -180:
            dec_longitude += 360

        while dec_longitude >= 180:
            dec_longitude -= 360

        self.lat = dec_latitude / 180
        self.lon = dec_longitude / 360
        self.precision = precision
        super(Geohash, self).__init__()
        self.encode(self.precision)

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

    def encode(self, precision=None):
        precision = precision or self.precision
        lat_length = lon_length = precision * 5 // 2
        lon_length += precision & 1

        # Here is where we decide encoding based on quadrant..
        # points near the equator, for example, will have widely
        # differing hashes because of this
        if self.lat > 0:
            lat = int((1 << lat_length) * self.lat) + (1 << (lat_length - 1))
        else:
            lat = (1 << lat_length - 1) - int((1 << lat_length) * -self.lat)

        if self.lon > 0:
            lon = int((1 << lon_length) * self.lon) + (1 << (lon_length - 1))
        else:
            lon = (1 << lon_length - 1) - int((1 << lon_length) * -self.lon)

        self.hash = self._encode_i2c(lat, lon, lat_length, lon_length)

    def decode(self):
        return (self.latitude, self.longitude)

    def __int__(self):
        pass

    def __float__(self):
        pass

    def hex(self):
        pass

    def unit_distance(self, lat1, lon1, lat2, lon2):
        degrees_to_radians = Decimal(math.pi) / 180
        phi1 = (90 - lat1) * degrees_to_radians
        phi2 = (90 - lat2) * degrees_to_radians
        theta1 = lon1 * degrees_to_radians
        theta2 = lon2 * degrees_to_radians

        # Compute spherical distance from spherical coordinates.
        cos = (
            math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2) +
            math.cos(phi1) * math.cos(phi2))

        return Decimal(math.acos(cos))

    def distance(self, other_hash):
        lat, lon = self.latitude, self.longitude
        other_lat, other_lon = other_hash.latitude, other_hash.longitude
        return self.unit_distance(lat, lon, other_lat, other_lon)

    def distance_in_miles(self, other_hash):
        return self.distance(other_hash) * 3960

    def distance_in_km(self, other_hash):
        return self.distance(other_hash) * 6373
