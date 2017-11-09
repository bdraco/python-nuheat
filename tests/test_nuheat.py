import json
import responses
import urllib

from nuheat import NuHeat, NuHeatThermostat, config
from mock import patch
from . import NuTestCase

class TestNuHeat(NuTestCase):

    def test_init_with_session(self):
        existing_session_id = "passed-session"
        api = NuHeat("test@example.com", "secure-password", existing_session_id)
        self.assertEqual(api.session_id, existing_session_id)

    @responses.activate
    def test_successful_authentication(self):
        response_data = self.load_fixture("auth_success.json")
        responses.add(
            responses.POST,
            config.AUTH_URL,
            status=200,
            body=json.dumps(response_data),
            content_type="application/json"
        )

        api = NuHeat("test@example.com", "secure-password")
        self.assertIsNone(api.session_id)
        api.authenticate()
        self.assertEqual(api.session_id, response_data.get("SessionId"))

    @responses.activate
    def test_authentication_error(self):
        response_data = self.load_fixture("auth_error.json")
        responses.add(
            responses.POST,
            config.AUTH_URL,
            status=200,
            body=json.dumps(response_data),
            content_type="application/json"
        )

        api = NuHeat("test@example.com", "secure-password")
        with self.assertRaises(Exception) as _:
            api.authenticate()
            self.assertIsNone(api.session_id)

    def test_authentication_failure(self):
        # TODO: 401, expired session
        pass

    @patch("nuheat.NuHeatThermostat.get_data")
    def test_get_thermostat(self, _):
        api = NuHeat(None, None)
        serial_number = "serial-123"
        thermostat = api.get_thermostat(serial_number)
        self.assertTrue(isinstance(thermostat, NuHeatThermostat))

    @responses.activate
    def test_get_request(self):
        url = "http://www.example.com/api"
        params = dict(test="param")
        responses.add(
            responses.GET,
            url,
            status=200,
            content_type="application/json"
        )
        api = NuHeat(None, None)
        response = api.request(url, method="GET", params=params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, "{}?{}".format(url, urllib.urlencode(params)))
        request_headers = response.request.headers
        self.assertEqual(request_headers["Origin"], config.REQUEST_HEADERS["Origin"])
        self.assertEqual(request_headers["Content-Type"], config.REQUEST_HEADERS["Content-Type"])

    @responses.activate
    def test_post_request(self):
        url = "http://www.example.com/api"
        params = dict(test="param")
        data = dict(test="data")
        responses.add(
            responses.POST,
            url,
            status=200,
            content_type="application/json"
        )
        api = NuHeat(None, None)
        response = api.request(url, method="POST", data=data, params=params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, "{}?{}".format(url, urllib.urlencode(params)))
        self.assertEqual(response.request.body, urllib.urlencode(data))
        request_headers = response.request.headers
        self.assertEqual(request_headers["Origin"], config.REQUEST_HEADERS["Origin"])
        self.assertEqual(request_headers["Content-Type"], config.REQUEST_HEADERS["Content-Type"])