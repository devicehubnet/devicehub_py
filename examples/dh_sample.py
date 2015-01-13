#!/usr/bin/env python
__author__ = 'Ionut Cotoi'
from lib.devicehub.http_api import Sensor, Actuator

dh_settings = {
    'project_id': 370,
    'api_key': '71f3dc5c-3f05-47bd-836b-cb0b85d11545',
}

temperature = Sensor(dh_settings, sensor_id=782)
humidity = Sensor(dh_settings, sensor_id=783)

led = Actuator(dh_settings, actuator_id=203)
servo = Actuator(dh_settings, actuator_id=204)
