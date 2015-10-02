#!/usr/bin/python
__author__ = 'Ionut Cotoi'
import paho.mqtt.client as mqtt
from time import sleep, time
from datetime import datetime
import json
import pickle
import os
import requests
from math import isinf, isnan


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
        if self.persistent:
            self.load()

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
                print e
        else:
            print "Project's persistent flag is not set. Will not import."

class Device(object):
    def __init__(self, project, device_uuid, api_key, debug_log=None):
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
        self.logger = None
        self.debug_log_file = debug_log

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

        self.client.connect("mqtt.devicehub.net", 1883, 10)
        self.client.loop_start()

        self.mqtt_connected = False
        self.initial_connect = False
        self.logged_disconnect = False

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        """

        :param client:
        :param userdata:
        :param flags:
        :param rc:
        """
        if self.initial_connect:
            payload = "Reconnected to the MQTT server with result code " + str(rc) + ". Going into online mode."
            for k, sen in self.actuators.items():
                self.client.subscribe(sen['topic'])
        else:
            payload = "Connected to the MQTT server with result code " + str(rc)
        print payload
        if self.logger:
            self.logger.addValue(payload)
        if self.debug_log_file:
            with open(self.debug_log_file, 'a') as f: f.write('\n' + str(datetime.now()) + ' - ' + payload)
        self.mqtt_connected = True
        self.bulkSend()

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.initial_connect = True

    def on_subscribe(self, client, userdata, mid, granted_qos):
        """

        :param client:
        :param userdata:
        :param mid:
        :param granted_qos:
        """
        # print("Subscribed to topic", client, userdata, mid, granted_qos)
        pass

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        """

        :param client:
        :param userdata:
        :param msg:
        """
        payload = "Received message on " + msg.topic+" - "+str(msg.payload)
        print payload
        if self.logger:
            self.logger.addValue(payload)
        if self.debug_log_file:
            with open(self.debug_log_file, 'a') as f: f.write('\n' + str(datetime.now()) + ' - ' + payload)

    def on_disconnect(self, client, userdata, rc):
        """

        :param client:
        :param userdata:
        :param rc:
        """
        payload = "Disconnected. Going into offline mode."
        print payload
        if self.logger:
            self.logger.addValue("Disconnected. Going into offline mode.")
        if self.debug_log_file:
            with open(self.debug_log_file, 'a') as f: f.write('\n' + str(datetime.now()) + ' - ' + payload)
        self.mqtt_connected = False
        self.project.persistent = True      # Set the project as persistent and save data to disk
        self.project.store()
        try:
            client.connect("mqtt.devicehub.net", 1883, 10)
        except:
            pass

    def getTopicRoot(self):
        """


        :return:
        """
        return '/a/' + self.api_key + '/p/' + str(self.project.project_id) + '/d/' + self.device_uuid + '/'

    def addSensor(self, sensor, logger=False):
        """

        :param sensor:
        :param logger:
        """
        if logger:
            if sensor.type == Sensor.STRING:
                self.logger = sensor
            else:
                payload = "Error. '{0}' is not a string sensor and cannot be used for device logging.".format(sensor.name)
                print payload
                if self.debug_log_file:
                    with open(self.debug_log_file, 'a') as f: f.write('\n' + str(datetime.now()) + ' - ' + payload)
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
            actuator.callback = callback
        self.client.message_callback_add(self.actuators[actuator.name]['topic'], actuator.default_callback)

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
                            if self.debug_log_file:
                                with open(self.debug_log_file, 'a') as f: f.write('\n' + str(datetime.now()) + ' - ' + e)
        else:
            if self.logger and not self.logged_disconnect:
                self.logger.addValue('Tried to send data without being connected to MQTT server.')
                self.logged_disconnect = True
            payload = 'Not connected to MQTT broker.'
            print payload
            if self.debug_log_file:
                with open(self.debug_log_file, 'a') as f: f.write('\n' + str(datetime.now()) + ' - ' + payload)
            try:
                self.client.connect("mqtt.devicehub.net", 1883, 10)
            except:
                pass
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
                payload = 'Error sending bulk data. Received request status code {0} with the following error message: {1}.'
                payload = payload.format(str(response.status_code), response.content)
                print payload
                if self.logger:
                    self.logger.addValue(payload)
                if self.debug_log_file:
                    with open(self.debug_log_file, 'a') as f: f.write('\n' + str(datetime.now()) + ' - ' + payload)
            else:
                for sensor_name in self.sensors:
                    self.sensors[sensor_name]['sensor'].values = []
        else:
            payload = 'Device is offline. Cannot send bulk data.'
            print payload
            if self.logged_disconnect and not self.logged_disconnect:
                self.logger.addValue(payload)
                self.logged_disconnect = True
            if self.debug_log_file:
                with open(self.debug_log_file, 'a') as f: f.write('\n' + str(datetime.now()) + ' - ' + payload)
            try:
                self.client.connect("mqtt.devicehub.net", 1883, 10)
            except:
                pass
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
        if self.type in (self.ANALOG, self.DIGITAL) and (isinf(value) or isnan(value)):
            print "Can't add value:", value
            if self.device and self.device.logger:
                self.device.logger.addValue("Sensor {0} tried to send illegal value: {1}".format(self.name, str(value)))
            return None
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
        self.state = None
        self.device = None
        self.callback = None

    def default_callback(self, *args):
        message = args[2].payload
        try:
            payload = json.loads(message)
            self.state = payload['state']
        except ValueError:
            payload = 'Error decoding actuator payload: ' + message
            print payload
            if self.device.logger:
                self.device.logger.addValue(payload)
            if self.device.debug_log_file:
                with open(self.device.debug_log_file, 'a') as f: f.write('\n' + str(datetime.now()) + ' - ' + payload)
        if self.callback:
            self.callback(payload)

