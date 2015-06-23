#!/usr/bin/python
__author__ = 'Ionut Cotoi'
import paho.mqtt.client as mqtt
from time import sleep, time
import json
import pickle
import os
import requests


class Project(object):
    def __init__(self, project_id, persistent=True):
        """

        :param project_id:
        :param persistent:
        """
        self.project_id = project_id
        self.devices = {}
        self.filename = 'proj_{0}_datastore.pkl'.format(str(project_id))
        self.persistent = persistent

    def store(self):
        if self.persistent:
            try:
                os.remove(self.filename + '.bak')
            except OSError as e:
                if e.errno == 2:
                    pass
                else:
                    raise e
            try:
                os.rename(self.filename, self.filename + '.bak')
            except OSError as e:
                if e.errno == 2:
                    pass
                else:
                    raise e
            # try:
            payload = {}
            for uuid, device in self.devices.items():
                for sensor_name in device.sensors:
                    print sensor_name
                    payload.update(
                        {
                            device.device_uuid: {
                                sensor_name: device.sensors[sensor_name]['sensor'].values
                            }
                        }
                    )
            f = open(self.filename, 'wb')
            f.write(pickle.dumps(payload, protocol=2))
            f.close()

    def load(self):
        if self.persistent:
            try:
                f = open(self.filename, 'rb')
                loaded_devices = pickle.load(f)
                f.close()
                for uuid, device in self.devices.items():
                    for sensor_name in device.sensors:
                        try:
                            device.sensors[sensor_name]['sensor'].values = loaded_devices[uuid][sensor_name]
                        except KeyError:
                            pass
            except Exception as e:
                raise e
        else:
            raise AttributeError("Project's persistent flag is not set. Will not import.")

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
        project.devices.update(
            {
                self.device_uuid: self
            }
        )

        self.sensors = {}
        self.actuators = {}

        self.http_api_url = 'https://api.devicehub.net/v2/project/' + str(self.project.project_id) + '/device/' + self.device_uuid + '/data'
        self.http_api_headers = {
            'Content-type': 'application/json',
            'X-ApiKey':     self.api_key
        }

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.client.connect("mqtt.devicehub.net", 1883, 60)
        self.client.loop_start()

        self.mqtt_connected = False
        self.initial_connect = False

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
        self.bulkSend()

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        if self.initial_connect:
            for k, sen in self.actuators.items():
                self.client.subscribe(sen['topic'])
        self.initial_connect = True

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
        print("Disconnected. Going into offline mode.")
        self.mqtt_connected = False
        self.project.persistent = True      # Set the project as persistent and save data to disk
        self.project.store()
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
        sensor.device = self

    def addActuator(self, actuator, callback=None):
        """

        :param actuator:
        :param callback:
        """
        self.actuators[actuator.name] = {
            'actuator': actuator,
            'topic':    self.getTopicRoot() + 'actuator/' + actuator.name + '/state'
        }
        actuator.device = self

        while self.mqtt_connected == False:
            sleep(0.5)

        self.client.subscribe(self.actuators[actuator.name]['topic'])

        if callback is not None:
            self.client.message_callback_add(self.actuators[actuator.name]['topic'], callback)

    def send(self):
        """


        """
        if self.mqtt_connected:
            for k, sen in self.sensors.items():
                if len(sen['sensor'].values):
                    for idx, sensor_value in enumerate(sen['sensor'].values):
                        value = sensor_value['value']
                        data = {
                            "timestamp": sensor_value['timestamp'],
                            "value": value
                        }
                        self.client.publish(sen['topic'], json.dumps(data))
                        try:
                            sen['sensor'].values.pop(idx)
                            self.project.store()
                        except Exception as e:
                            print e
        else:
            print 'Not connected to MQTT broker.'
            # raise IOError('Not connected to MQTT broker.')

    def bulkSend(self):
        """


        """
        if self.mqtt_connected:
            payload = {
                'sensors':      {},
                'actuators':    {},
            }
            for sensor_name in self.sensors:
                values = {value['timestamp']: value['value'] for value in self.sensors[sensor_name]['sensor'].values}
                payload['sensors'].update(
                    {
                        sensor_name: values
                    }
                )
            response = requests.post(self.http_api_url, data=json.dumps(payload), headers=self.http_api_headers)
            if response.status_code != 200:
                print response.content
                raise requests.HTTPError('Error sending data. Try again later.')
            else:
                for sensor_name in self.sensors:
                    self.sensors[sensor_name]['sensor'].values = []
        else:
            print 'Device is offline.'
            # raise IOError('Device is offline.')


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
        self.device = None
        self.values = []

    def addValue(self, value):
        # print(self.name, value)
        self.values.append(dict(timestamp=time(), value=value))
        self.device.project.store()


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
        self.device = None
