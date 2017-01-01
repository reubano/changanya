#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
changanya
~~~~~~~~~

Provides interesting (non-cryptographic) hashes implemented in pure Python

Included so far:

 * Bloom filters
 * Simhash (Charikar similarity hashes)
 * Nilsimsa signatures
 * Geohash
"""

from datetime import date

__version__ = '0.5.0'
__title__ = 'changanya'
__package_name__ = 'changanya'
__author__ = 'Reuben Cummings'
__description__ = 'Library of interesting pure Python non-cryptographic hashes'
__email__ = 'reubano@gmail.com'
__license__ = 'MIT'
__copyright__ = 'Copyright %i Reuben Cummings' % date.today().year
