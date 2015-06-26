#!/usr/bin/env python
from devicehub.devicehub import Sensor, Actuator, Device, Project
from random import randint
from time import sleep

import json
import mraa

led_x = mraa.Gpio(13) # onboard led
led_x.dir(mraa.DIR_OUT)

PROJECT_ID = '1234'
DEVICE_UUID = '1234567-daa7-4c25-89e2-fa32164d5c16'
API_KEY = '1234567-5131-407f-b76f-5158fa1234567'

act_state = 0

def on_led(client, userdata, message):
    msg = str(message.payload)
    j = json.loads(msg)
    global act_state
    act_state = int(j['state'])
    print message.payload


def on_servo(client, userdata, message):
    print message.payload


project = Project(PROJECT_ID, persistent=True)

device = Device(project, DEVICE_UUID, API_KEY)

temperature = Sensor(Sensor.ANALOG, 'Temperature')
humidity = Sensor(Sensor.ANALOG, 'Humidity')

led = Actuator(Actuator.DIGITAL, 'LED')
servo = Actuator(Actuator.ANALOG, 'SERVO')

device.addSensor(temperature)
device.addSensor(humidity)

device.addActuator(led, on_led)
device.addActuator(servo, on_servo)


while True:
    temperature.addValue(randint(1, 100))
    humidity.addValue(randint(1, 100))
    device.send()
    
    if act_state:
        led_x.write(1)
    else:
        led_x.write(0)

    sleep(1)




