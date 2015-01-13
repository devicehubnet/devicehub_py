__author__ = 'Ionut Cotoi'
from urllib import urlencode
import json

from devicehub.objects import Endpoint, POST_URLENCODED, ENDPOINT_ERR



# HTTP JSON API test classes
class Sensor(Endpoint):
    def __init__(self, settings, sensor_id, project_id=None):
        """


        """
        if project_id is None:
            project_id = settings['project_id']

        super(Sensor, self).__init__(settings, project_id, sensor_id)
        self.api_endpoint = self.api_endpoint_root
        self.api_endpoint += "/project/" + str(self.project_id) + "/sensor/" + str(self.endpoint_id) + "/"

    def set(self, value, method=POST_URLENCODED):
        """

        :param value:
        :return:
        """

        data = {
            "apiKey": self.settings['api_key'],
            "value": value,
        }

        data = urlencode(data)

        # print "API endpoint:", api_endpoint
        # print "data:", data

        resp, content = self.h.request(self.api_endpoint, "POST", data, {'Content-type': 'application/x-www-form-urlencoded'})

        # print "resp:", resp
        # print "content:", content
        if resp['status'] == '200':
            return 0
        else:
            return ENDPOINT_ERR

    def set_multi(self, dict):
        # TODO
        pass

    def get(self):
        """


        :return:
        """
        data = {
            "apiKey": self.api_key,
            "limit": 1,
        }

        resp, content = self.h.request(self.api_endpoint + "?" + urlencode(data), "GET")

        # print "resp:", resp
        # print "content:", content

        result = json.loads(content)

        if len(result) != 1:
            return ENDPOINT_ERR
        else:
            result = result[0]

        if resp['status'] == '200':
            return float(result['value'])
        else:
            return ENDPOINT_ERR


class Actuator(Endpoint):
    def __init__(self, settings, actuator_id, project_id=None):
        """


        """
        if project_id is None:
            project_id = settings['project_id']

        super(Actuator, self).__init__(settings, project_id, actuator_id)
        self.api_endpoint = self.api_endpoint_root
        self.api_endpoint += "/project/" + str(self.project_id) + "/actuator/" + str(self.endpoint_id) + "/"

    def set(self, value, method=POST_URLENCODED):
        """

        :param value:
        :return:
        """
        data = {
            "apiKey": self.settings['api_key'],
            "state": value,
        }

        data = urlencode(data)

        # print "API endpoint:", api_endpoint
        # print "data:", data

        resp, content = self.h.request(self.api_endpoint, "POST", data, {'Content-type': 'application/x-www-form-urlencoded'})

        # print "resp:", resp
        # print "content:", content
        if resp['status'] == '200':
            return 0
        else:
            return ENDPOINT_ERR

    def get(self):
        """


        :return:
        """
        data = {
            "apiKey": self.api_key,
        }

        resp, content = self.h.request(self.api_endpoint + "?" + urlencode(data), "GET")

        # print "resp:", resp
        # print "content:", content

        result = json.loads(content)

        if resp['status'] == '200':
            return result['state']
        else:
            return ENDPOINT_ERR