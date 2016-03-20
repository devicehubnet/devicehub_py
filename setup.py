#!/usr/bin/env python
__author__ = 'Ionut Cotoi'
from distutils.core import setup

setup(name='devicehub',
      version='0.8.7',
      package_dir={'devicehub': 'devicehub'},
      packages=['devicehub'],
      install_requires=['httplib2', 'paho-mqtt', 'requests'],
      url='https://devicehub.net',
      maintainer='Cristian Gociu', maintainer_email='cristi@devicehub.net',
      description='DeviceHub python library for v1 APIs',
     )
