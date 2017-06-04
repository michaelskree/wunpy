import datetime
import responses
from unittest import mock, TestCase
from wunpy import api, cache
from xml.etree import ElementTree


class APITest(TestCase):

    @responses.activate
    def test_error(self):
        uri = "http://api.wunderground.com/api/key/conditions/q/12345.json"
        resp = {
            "response": {
                "error": {
                    "description": "Unknown location",
                },
            },
        }
        responses.add(responses.GET, uri, json=resp)
        wapi = api.API("key")
        with self.assertRaises(api.APIError) as cm:
            wapi.conditions(12345)
        self.assertEqual(str(cm.exception), "Unknown location")

        uri = "http://api.wunderground.com/api/key/conditions/q/12345.xml"
        resp = "<response><error><description>Unknown location</description></error></response>"
        responses.add(responses.GET, uri, body=resp)
        wapi = api.API("key", resp_format="xml")
        with self.assertRaises(api.APIError) as cm:
            wapi.conditions(12345)
        self.assertEqual(str(cm.exception), "Unknown location")

    @responses.activate
    def test_feature(self):
        uri = "http://api.wunderground.com/api/key/conditions/q/12345.json"
        resp = {
            "response": {},
            "current_observation": {
                "key": "value",
            },
        }
        responses.add(responses.GET, uri, json=resp)
        wapi = api.API("key")
        results = wapi.conditions(12345)
        self.assertEqual(results, resp)

        uri = "http://api.wunderground.com/api/key/conditions/q/12345.xml"
        resp = "<response><current_observation><element>Value</element></current_observation></response>"
        responses.add(responses.GET, uri, body=resp)
        wapi = api.API("key", resp_format="xml")
        results = wapi.conditions(12345)
        text = str(ElementTree.tostring(results), "utf-8")
        self.assertEqual(text, resp)

    @responses.activate
    def test_multi_feature(self):
        uri = "http://api.wunderground.com/api/key/conditions/forecast/q/12345.json"
        resp = {
            "response": {},
            "current_observation": {
                "key": "value",
            },
            "forecast": {
                "key": "value",
            },
        }
        responses.add(responses.GET, uri, json=resp)
        wapi = api.API("key")
        results = wapi.get(["conditions", "forecast"], 12345)
        self.assertEqual(results, resp)

    @responses.activate
    def test_current_hurricane(self):
        uri = "http://api.wunderground.com/api/key/currenthurricane/view.json"
        resp = {
            "response": {},
            "currenthurricane": {
                "key": "value",
            },
        }
        responses.add(responses.GET, uri, json=resp)
        wapi = api.API("key")
        results = wapi.current_hurricane()
        self.assertEqual(results, resp)

    @responses.activate
    def test_history(self):
        uri = "http://api.wunderground.com/api/key/history_20170101/q/12345.json"
        resp = {
            "response": {},
            "history_20170101": {
                "key": "value",
            },
        }
        responses.add(responses.GET, uri, json=resp)
        wapi = api.API("key")
        results = wapi.history(12345, datetime.date(2017, 1, 1))
        self.assertEqual(results, resp)

    def test_get_cached(self):
        c = cache.Cache()
        c.get = mock.Mock(return_value={"key": "value"})
        wapi = api.API("key", cache=c)
        results = wapi.conditions(12345)
        self.assertEqual(results["key"], "value")

    @responses.activate
    def test_get_uncached(self):
        uri = "http://api.wunderground.com/api/key/conditions/q/12345.json"
        resp = {
            "response": {},
            "current_observation": {
                "key": "value",
            },
        }
        responses.add(responses.GET, uri, json=resp)
        c = cache.Cache()
        c.get = mock.Mock(return_value=None)
        c.set = mock.Mock()
        wapi = api.API("key", cache=c)
        results = wapi.conditions(12345)
        self.assertEqual(results, resp)
        c.set.assert_called_with(uri, resp)

    def test_invalid_feature(self):
        wapi = api.API("key")
        with self.assertRaises(AttributeError):
            wapi.invalid(12345)

    def test_invalid_response_format(self):
        with self.assertRaises(ValueError):
            api.API("key", resp_format="invalid")
