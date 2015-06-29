#!/usr/bin/env python
from devicehub.devicehub import Sensor, Actuator, Device, Project
from random import randint
from time import sleep


PROJECT_ID = '1234'
DEVICE_UUID = '1234567-daa7-4c25-89e2-fa32164d5c16'
API_KEY = '1234567-5131-407f-b76f-5158fa1234567'


def on_led(data):
    """
    Whenever an actuator receives a command from DeviceHub.net, it's state property is updated.
    The received data is also passed to the callback as a dictionary consisting of 'timestamp' and 'state'.
    timestamp - contains the unix timestamp at which the actuator was commanded
    state - contains the new actuator state
    """
    print 'Received command to toggle the LED to', led.state


def on_servo(data):
    print 'Received command to set the servo to', servo.state


# We want the data to be saved to disk before sending it to DeviceHub.net so we're setting persistent to True
# This also ensures that the project data stored locally is loaded if it exists.
project = Project(PROJECT_ID, persistent=True)

device = Device(project, DEVICE_UUID, API_KEY)

temperature = Sensor(Sensor.ANALOG, 'Temperature')
humidity = Sensor(Sensor.ANALOG, 'Humidity')
log = Sensor(Sensor.STRING, 'Log')

led = Actuator(Actuator.DIGITAL, 'LED')
servo = Actuator(Actuator.ANALOG, 'SERVO')

# Passing logger=True also sends all log output to this string sensor.
device.addSensor(log, logger=True)
device.addSensor(temperature)
device.addSensor(humidity)

device.addActuator(led, on_led)
device.addActuator(servo, on_servo)


log.addValue('Device initialized successfully.')
while True:
    temperature.addValue(randint(1, 100))
    humidity.addValue(randint(1, 100))
    device.send()
    sleep(1)




