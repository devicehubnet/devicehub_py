#!/usr/bin/python
__author__ = 'Ionut Cotoi'
import paho.mqtt.client as mqtt
from time import sleep, time
import json


class Project(object):
    def __init__(self, project_id):
        """

        :param project_id:
        """
        self.project_id = project_id


class Device(object):
    def __init__(self, project, device_uuid, api_key):
        """

        :param project:
        :param device_uuid:
        :param api_key:
        """
        self.project = project
        self.device_uuid = device_uuid
        self.api_key = api_key

        self.sensors = {}
        self.actuators = {}

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.client.connect("mqtt.devicehub.net", 1883, 60)
        self.client.loop_start()

        self.mqtt_connected = False

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        """

        :param client:
        :param userdata:
        :param flags:
        :param rc:
        """
        print("Connected with result code "+str(rc))
        self.mqtt_connected = True

        # TODO uncomment following in order to re-subribe to actuator topics on disconnect
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # for k, sen in self.actuators.items():
        #     self.client.subscribe(sen['topic'])

    def on_subscribe(self, client, userdata, mid, granted_qos):
        """

        :param client:
        :param userdata:
        :param mid:
        :param granted_qos:
        """
        print("Subscribed to topic", client, userdata, mid, granted_qos)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        """

        :param client:
        :param userdata:
        :param msg:
        """
        print(msg.topic+" "+str(msg.payload))

    def on_disconnect(self, client, userdata, rc):
        """

        :param client:
        :param userdata:
        :param rc:
        """
        print("disconnected")
        self.mqtt_connected = False
        client.connect()

    def getTopicRoot(self):
        """


        :return:
        """
        return '/a/' + self.api_key + '/p/' + str(self.project.project_id) + '/d/' + self.device_uuid + '/'

    def addSensor(self, sensor):
        """

        :param sensor:
        """
        self.sensors[sensor.name] = {
            'sensor': sensor,
            'topic':  self.getTopicRoot() + 'sensor/' + sensor.name + '/data'
        }

    def addActuator(self, actuator, callback=None):
        """

        :param actuator:
        :param callback:
        """
        self.actuators[actuator.name] = {
            'actuator': actuator,
            'topic':    self.getTopicRoot() + 'actuator/' + actuator.name + '/state'
        }

        while self.mqtt_connected == False:
            sleep(0.5)

        self.client.subscribe(self.actuators[actuator.name]['topic'])

        if callback is not None:
            self.client.message_callback_add(self.actuators[actuator.name]['topic'], callback)

    def send(self):
        """


        """
        for k, sen in self.sensors.items():
            if len(sen['sensor'].values):
                for idx, sensor_value in enumerate(sen['sensor'].values):
                    value = sensor_value['value']
                    data = {
                        "name": sensor_value['timestamp'],
                        "value": value
                    }
                    self.client.publish(sen['topic'], json.dumps(data))
                    try:
                        sen['sensor'].values.pop(idx)
                    except Exception as e:
                        print e

    def debug(self):
        """


        """
        print "\nSensors:"
        for k, sen in self.sensors.items():
            print (k)
            print (sen['topic'])

        print "\nActuators:"
        for k, act in self.actuators.items():
            print (k)
            print (act['topic'])
        print ""


class Sensor(object):
    DIGITAL = 'Digital'
    ANALOG = 'Analog'
    STRING = 'String'

    def __init__(self, sensor_type, sensor_name):
        """

        :param sensor_type:
        :param sensor_name:
        """
        self.type = sensor_type
        self.name = sensor_name
        self.values = []

    def addValue(self, value):
        # print(self.name, value)
        self.values.append(dict(timestamp=int(time() * 1000), value=value))


class Actuator(object):
    DIGITAL = 'Digital'
    ANALOG = 'Analog'

    def __init__(self, actuator_type, actuator_name):
        """

        :param actuator_type:
        :param actuator_name:
        """
        self.type = actuator_type
        self.name = actuator_name
