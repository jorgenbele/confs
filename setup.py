#!/bin/env python3
from setuptools import find_packages, setup, Command

setup(
    name             = 'confs',
    version          = '0.1',
    description      = 'Configuration file management utility',
    author           = 'blockdevice',
    url              = 'https://github.com/blockdevice/confs',
    package_dir      = {'': 'src'},
    packages         = ['confs'],
    entry_points     = {'console_scripts': ['confs = confs.__main__:main'],},
    install_requires = ['docopt'],
    classifiers      = [
        'Programming Language :: Python :: 3', 'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Utilities',
    ],
)
