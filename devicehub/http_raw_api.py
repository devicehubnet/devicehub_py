__author__ = 'cotty'
from objects import Endpoint, ENDPOINT_ERR
import httplib2
from urllib import urlencode


# HTTP RAW API test classes
class SensorRaw(Endpoint):
    def __init__(self, settings, project_id, sensor_id):
        """


        """
        super(SensorRaw, self).__init__(settings, project_id, sensor_id)

    def set(self, value):
        """

        :param value:
        :return:
        """
        h = httplib2.Http()
        api_endpoint = self.api_endpoint_root
        api_endpoint += "/" + str(self.project_id) + "/"
        data = {
            "apiKey": self.settings['api_key'],
            str(self.endpoint_id): value,
        }

        data = urlencode(data)

        # print "API endpoint:", api_endpoint
        # print "data:", data

        resp, content = h.request(api_endpoint, "POST", data, {'Content-type': 'application/x-www-form-urlencoded'})

        # print "resp:", resp
        # print "content:", content
        if resp['status'] == '200':
            return 0
            self.value = value
        else:
            return ENDPOINT_ERR

    def set_multi(self, dict):
        # TODO
        pass

    def get(self):
        """


        :return:
        """
        h = httplib2.Http()
        api_endpoint = self.api_endpoint_root
        api_endpoint += "/" + str(self.project_id) + "/sensor/" + str(self.endpoint_id) + "/"
        api_endpoint += "?apiKey="+self.api_key

        resp, content = h.request(api_endpoint, "GET")

        # print "resp:", resp
        # print "content:", content

        if resp['status'] == '200':
            try:
                self.value = float(content)
            except Exception as e:
                self.value = ENDPOINT_ERR
            else:
                return self.value
        else:
            return ENDPOINT_ERR


class ActuatorRaw(Endpoint):
    def __init__(self, settings, project_id, actuator_id):
        """


        """
        super(ActuatorRaw, self).__init__(settings, project_id, actuator_id)

    def set(self, value):
        """

        :param value:
        :return:
        """
        h = httplib2.Http()
        api_endpoint = self.api_endpoint_root
        api_endpoint += "/" + str(self.project_id) + "/actuator/" + str(self.endpoint_id) + "/"
        data = {
            "apiKey": self.api_key,
            "state": value,
        }

        data = urlencode(data)

        # print "API endpoint:", api_endpoint
        # print "data:", data

        resp, content = h.request(api_endpoint, "POST", data, {'Content-type': 'application/x-www-form-urlencoded'})

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
        h = httplib2.Http()
        api_endpoint = self.api_endpoint_root
        api_endpoint += "/" + str(self.project_id) + "/actuator/" + str(self.endpoint_id)
        api_endpoint += "?apiKey=" + self.api_key

        resp, content = h.request(api_endpoint, "GET")

        # print "resp:", resp
        # print "content:", content

        if resp['status'] == '200':
            return float(content)
        else:
            return ENDPOINT_ERR