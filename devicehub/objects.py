__author__ = 'cotty'
from enum import Enum
import httplib2
import paho.mqtt.client as mqtt
import time
import threading
import random


ENDPOINT_ERR = -9999


POST_JSON = 0
POST_URLENCODED = 1


class API_VARIANTS(Enum):
    HTTP_RAW  = "http_raw"
    HTTP_RAW_INDEX = 0
    HTTP_JSON = "http_json"
    HTTP_JSON_INDEX = 1
    MQTT_RAW  = "mqtt_raw"
    MQTT_RAW_INDEX = 2
    MQTT_JSON = "mqtt_json"
    MQTT_JSON_INDEX = 3


API = {
    "api_host": "www.devicehub.net",
    "api_root": "/io",
    "api_protocol": "http",
    "mqtt_read_timeout": 10,  # seconds
}


class Endpoint(object):
    """ Common base class for all IoT endpoints on DeviceHub.net """
    def __init__(self, settings, project_id, endpoint_id):
        """


        """
        self.project_id = project_id
        self.endpoint_id = endpoint_id
        self.settings = settings
        self.api = API

        for key in settings['api'].keys():
            self.api[key] = settings['api'][key]

        self.api_endpoint_root = self.api['api_protocol'] + "://" + self.api['api_host'] + self.api['api_root']
        self.api_key = self.settings['api_key']

        self.value = None

        self.h = httplib2.Http()

    def toggle_value(self):
        """


        """
        pass


class MQTTRawEndpoint(Endpoint):
    """ MQTT communication - common base class for all IoT endpoints on DeviceHub.net """
    def __init__(self, settings, project_id, endpoint_id):
        """


        """
        super(MQTTRawEndpoint, self).__init__(settings, project_id, endpoint_id)

        self.mqtt_client = mqtt.Client(client_id="dh_tests"+str(random.randint(0,1000)))
        self.mqtt_client.on_message = self.on_message
        # self.mqtt_client.loop_start()
        self.mqtt_client.connect(self.api['mqtt_host'], port=self.api['mqtt_port'])
        self.mqtt_connected = True

        # Start a loop thread async, that will run for a maximum of x seconds
        # i.e. will call disconnect
        self.t_start = None
        self.t = threading.Thread(target=self.mqtt_network_loop)
        self.t.start()

        self.mqtt_topic = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.t.join()

    def on_message(self, client, userdata, msg):
        # print(msg.topic + " " + str(msg.payload))
        self.value = float(msg.payload)

    def mqtt_network_loop(self):
        self.t_start = int(time.time())
        # print "Thread start time:", self.t_start

        while int(time.time()) < self.t_start + 5 and self.value is None:
            self.mqtt_client.loop()

        self.mqtt_client.disconnect()
        self.mqtt_connected = False
        # print "mqtt disconnect"

    def get(self):
        """


        :return:
        """
        self.value = None
        time.sleep(3)
        self.mqtt_client.subscribe(self.mqtt_topic)
        while self.value is None and self.mqtt_connected:
            # Block here until we have a value from the topic
            pass
        return self.value