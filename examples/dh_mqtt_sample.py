__author__ = 'Ionut Cotoi'
import paho.mqtt.client as mqtt
import random
from time import sleep
from devicehub.mqtt_api import Device, Sensor, Actuator


dh_settings = {
    'api_host': 'api.dev.devicehub.net',
    'mqtt_host': 'mqtt.dev.devicehub.net',
    'project_id': 44,
    'device_id': 71,
    'api_key': '71f3dc5c-3f05-47bd-836b-cb0b85d11545',
}


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("iot.eclipse.org", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

for i in range(10):
    temperature.set(round(random.random()*100, 3))
    humidity.set(round(random.random()*100, 3))
    sleep(1)

