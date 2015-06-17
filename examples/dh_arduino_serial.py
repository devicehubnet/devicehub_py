#!/usr/bin/env python
import serial
from devicehub.http_api import Sensor, Actuator


s = serial.Serial('COM10', 9600, timeout=1)

dh_settings = {
    'project_id': 370,
    'api_key': '71f3dc5c-3f05-47bd-836b-cb0b85d11545',
}

temperature = Sensor(dh_settings, sensor_id=782)
humidity = Sensor(dh_settings, sensor_id=783)

led = Actuator(dh_settings, actuator_id=203)
servo = Actuator(dh_settings, actuator_id=204)



# temperature.set(round(random.random()*100, 3))
# humidity.set(round(random.random()*100, 3))

# print "done"

while True:
    line = s.readline()
    print line
    line = line.split(" ")
    # print line
    try:
        hum = line[0].split(":")[1]
        temp = line[1].split(":")[1]

        hum = float(hum)
        temp = float(temp)

        # print hum
        # print temp
    except Exception as e:
        pass
    else:
        temperature.set(temp)
        humidity.set(hum)
    
        
    
