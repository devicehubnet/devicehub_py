__author__ = 'cotty'
from objects import MQTTRawEndpoint, ENDPOINT_ERR
from http_json_api import ActuatorJSON
import time


# MQTT RAW API test classes
class SensorMQTTRaw(MQTTRawEndpoint):
    def __init__(self, settings, project_id, sensor_id):
        """


        """
        super(SensorMQTTRaw, self).__init__(settings, project_id, sensor_id)

        self.mqtt_topic = "/" + self.api_key + "/" + str(project_id) + "/sensor/" + str(sensor_id)
        # print self.mqtt_topic

    def __exit__(self):
        super(SensorMQTTRaw, self).__exit__()

    def set(self, value):
        """

        :param value:
        :return:
        """
        self.mqtt_client.publish(self.mqtt_topic, str(value), qos=0, retain=True)
        return ENDPOINT_ERR


class ActuatorMQTTRaw(MQTTRawEndpoint):
    def __init__(self, settings, project_id, actuator_id):
        """


        """
        super(ActuatorMQTTRaw, self).__init__(settings, project_id, actuator_id)

        self.mqtt_topic = "/" + self.api_key + "/" + str(project_id) + "/actuator/" + str(actuator_id)

    def __exit__(self, type, value, traceback):
        super(ActuatorMQTTRaw, self).__exit__()

    def set(self, value):
        """

        :param value:
        :return:
        """

        # self.mqtt_client.publish(self.mqtt_topic, str(value), qos=0, retain=True)
        a = ActuatorJSON(self.settings, self.project_id, self.endpoint_id)
        a.set(int(value))
        # print "set", int(value)
        time.sleep(2)
        return ENDPOINT_ERR
