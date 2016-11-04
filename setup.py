#!/usr/bin/env python
__author__ = 'Ionut Cotoi'
from distutils.core import setup

setup(name='devicehub',
      version='0.8.8',
      package_dir={'devicehub': 'devicehub'},
      packages=['devicehub'],
      install_requires=['httplib2', 'paho-mqtt', 'urllib3'],
      url='https://devicehub.net',
      maintainer='Ionut Cotoi', maintainer_email='ionut@devicehub.net',
      description='DeviceHub python library for v2 APIs',
     )
