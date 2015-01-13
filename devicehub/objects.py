__author__ = 'Ionut Cotoi'
import httplib2

ENDPOINT_ERR = -9999


POST_JSON = 0
POST_URLENCODED = 1


API = {
    "api_host": "www.devicehub.net",
    "api_root": "/io",
    "api_protocol": "http",
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

        if 'api' in settings:
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
