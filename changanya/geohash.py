# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

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

Part of changanya by reubano. See README and LICENSE.
Based on code by Hiroaki Kawai <kawai@iij.ad.jp> and geohash.org
"""

import math

from decimal import Decimal
from changanya.hashtype import Hashtype

_BASE32 = '0123456789bcdefghjkmnpqrstuvwxyz'
_BASE32_MAP = {_BASE32[i]: i for i in range(len(_BASE32))}


# http://gis.stackexchange.com/q/115280/39422
# http://gis.stackexchange.com/a/8655/39422
# http://gis.stackexchange.com/a/208739/39422
LATLON_PRECISION_OFFSET = 2
HASH_PLACES_OFFSET = -LATLON_PRECISION_OFFSET
KM_PRECISION_OFFSET = 2
KM_PLACES_OFFSET = -KM_PRECISION_OFFSET
MI_PRECISION_OFFSET = 1
MI_PLACES_OFFSET = -MI_PRECISION_OFFSET


# TODO: account for 2nd link and cases where displayed decimal places < 0
class Geohash(Hashtype):
    # Not the actual RFC 4648 standard; a variation
    def __init__(self, latitude=0, longitude=0, precision=8):
        dec_latitude = Decimal(latitude)
        dec_longitude = Decimal(longitude)

        if dec_latitude >= 90 or dec_latitude < -90:
            raise ValueError('invalid latitude %s' % latitude)

        self.lat_places = -dec_latitude.as_tuple()[2]
        self.lon_places = -dec_longitude.as_tuple()[2]
        self.max_precision = max(self.lat_places + HASH_PLACES_OFFSET, 0)
        self.other_max_precision = None
        self.precision = min(self.max_precision, precision)
        self.latitude = dec_latitude
        self.longitude = dec_longitude

        while dec_longitude < -180:
            dec_longitude += 360

        while dec_longitude >= 180:
            dec_longitude -= 360

        self.lat = dec_latitude / 180
        self.lon = dec_longitude / 360
        super(Geohash, self).__init__()
        self.encode()

    @property
    def lat_precision(self):
        precision = self.precision + LATLON_PRECISION_OFFSET
        return Decimal((0, (1,), -min(precision, self.lat_places)))

    @property
    def lon_precision(self):
        precision = self.precision + LATLON_PRECISION_OFFSET
        return Decimal((0, (1,), -min(precision, self.lon_places)))

    @property
    def distance_precision(self):
        return min(self.precision, self.other_max_precision)

    @property
    def km_precision(self):
        precision = self.distance_precision + KM_PRECISION_OFFSET
        return Decimal((0, (1,), -precision))

    @property
    def mi_precision(self):
        precision = self.distance_precision + MI_PRECISION_OFFSET
        return Decimal((0, (1,), -precision))

    def _encode_i2c(self, lat, lon, lat_length, lon_length):
        precision = (lat_length + lon_length) // 5
        a, b = (lon, lat) if lat_length < lon_length else (lat, lon)
        boost = (0, 1, 4, 5, 16, 17, 20, 21)
        ret = ''

        for i in range(precision):
            ret += _BASE32[(boost[a & 7] + (boost[b & 3] << 1)) & 0x1F]
            a, b = b >> 2, a >> 3

        return ret[::-1]

    def encode(self, precision=None):
        self.precision = min(precision or self.precision, self.max_precision)
        lat_length = lon_length = self.precision * 5 // 2
        lon_length += self.precision & 1

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

    def _decode_c2i(self, _hash):
        def magic(x, y, x_length, y_length, t):
            x = x << 3
            y = y << 2
            x += (t >> 2) & 4
            y += (t >> 2) & 2
            x += (t >> 1) & 2
            y += (t >> 1) & 1
            x += t & 1
            x_length += 3
            y_length += 2
            return (x, y, x_length, y_length)

        lon = 0
        lat = 0
        bit_length = 0
        lat_length = 0
        lon_length = 0

        # Unrolled for speed and clarity
        for i in _hash:
            t = _BASE32_MAP[i]

            if bit_length & 1:
                lat, lon, lat_length, lon_length = magic(
                    lat, lon, lat_length, lon_length, t)
            else:
                lon, lat, lon_length, lat_length = magic(
                    lon, lat, lon_length, lat_length, t)

            bit_length += 5

        lat = lat << 1
        lon = lon << 1
        lat_length += 1
        lon_length += 1
        lat_numerator = Decimal(lat - (1 << (lat_length - 1)))
        lon_numerator = Decimal(lon - (1 << (lon_length - 1)))
        latitude = 180 * lat_numerator / (1 << lat_length)
        longitude = 360 * lon_numerator / (1 << lon_length)
        return (latitude, longitude)

    def decode(self, _hash=None):
        if _hash:
            latitude, longitude = self._decode_c2i(_hash)
        else:
            latitude, longitude = self.latitude, self.longitude

        quantized_lat = latitude.quantize(self.lat_precision)
        quantized_lon = longitude.quantize(self.lon_precision)
        return (quantized_lat, quantized_lon)

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

    def distance(self, other):
        self.other_max_precision = other.max_precision
        lat, lon = self.latitude, self.longitude
        other_lat, other_lon = other.latitude, other.longitude
        return self.unit_distance(lat, lon, other_lat, other_lon)

    def distance_in_miles(self, other):
        distance = (self.distance(other) * 3960).quantize(self.mi_precision)
        return distance

    def distance_in_km(self, other):
        distance = (self.distance(other) * 6373).quantize(self.km_precision)
        return distance
