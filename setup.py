#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='changanya',
    version='0.3.1',
    description='Library of interesting (non-cryptographic) hashes in pure Python.',
    author='reubano',
    author_email='reubano@gmail.com',
    url='http://github.com/reubano/changanya',
    download_url='http://github.com/reubano/changanya/downloads',
    packages=find_packages(),
    install_requires=[],
    test_suite='nose.collector',
    tests_require=['nose>=1.3.7,<2.0.0'],
    license=license,
    zip_safe=False,
    keywords=[
        'hash', 'bloom filter', 'geohash', 'nilsimsa', 'simhash', 'charikar'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Environment :: Console',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ],
    platforms=['MacOS X', 'Windows', 'Linux'],
)
