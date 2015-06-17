#!/usr/bin/env python
__author__ = 'Ionut Cotoi'
from distutils.core import setup

setup(name='devicehub',
      version='0.6',
      package_dir={'devicehub': 'devicehub'},
      packages=['devicehub'],
      install_requires=['httplib2', 'paho-mqtt'],
     )
