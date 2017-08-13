import datetime
import responses
from unittest import mock, TestCase
from wunpy import api, cache
from xml.etree import ElementTree


class APITest(TestCase):

    @responses.activate
    def test_error(self):
        uri = "http://api.wunderground.com/api/key/alerts/lang:EN/q/12345.json"
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
            wapi.alerts(12345)
        self.assertEqual(str(cm.exception), "Unknown location")

        uri = "http://api.wunderground.com/api/key/alerts/lang:EN/q/12345.xml"
        resp = "<response><error><description>Unknown location</description></error></response>"
        responses.add(responses.GET, uri, body=resp)
        wapi = api.API("key", resp_format="xml")
        with self.assertRaises(api.APIError) as cm:
            wapi.alerts(12345)
        self.assertEqual(str(cm.exception), "Unknown location")

    @responses.activate
    def test_feature(self):
        uri = "http://api.wunderground.com/api/key/alerts/lang:EN/q/12345.json"
        resp = {
            "response": {},
            "alerts": [],
        }
        responses.add(responses.GET, uri, json=resp)
        wapi = api.API("key")
        results = wapi.alerts(12345)
        self.assertEqual(results, resp)

        uri = "http://api.wunderground.com/api/key/alerts/lang:EN/q/12345.xml"
        resp = "<response><alerts /></response>"
        responses.add(responses.GET, uri, body=resp)
        wapi = api.API("key", resp_format="xml")
        results = wapi.alerts(12345)
        text = str(ElementTree.tostring(results), "utf-8")
        self.assertEqual(text, resp)

    @responses.activate
    def test_multi_feature(self):
        uri = "http://api.wunderground.com/api/key/alerts/forecast/lang:EN/q/12345.json"
        resp = {
            "response": {},
            "alerts": [],
            "forecast": {
                "key": "value",
            },
        }
        responses.add(responses.GET, uri, json=resp)
        wapi = api.API("key")
        results = wapi.get(["alerts", "forecast"], 12345)
        self.assertEqual(results, resp)

    @responses.activate
    def test_current_hurricane(self):
        uri = "http://api.wunderground.com/api/key/currenthurricane/lang:EN/view.json"
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
        uri = "http://api.wunderground.com/api/key/history_20170101/lang:EN/q/12345.json"
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
        results = wapi.alerts(12345)
        self.assertEqual(results["key"], "value")

    @responses.activate
    def test_get_uncached(self):
        uri = "http://api.wunderground.com/api/key/alerts/lang:EN/q/12345.json"
        resp = {
            "response": {},
            "alerts": [],
        }
        responses.add(responses.GET, uri, json=resp)
        c = cache.Cache()
        c.get = mock.Mock(return_value=None)
        c.set = mock.Mock()
        wapi = api.API("key", cache=c)
        results = wapi.alerts(12345)
        self.assertEqual(results, resp)
        c.set.assert_called_with(uri, resp)

    def test_invalid_feature(self):
        wapi = api.API("key")
        with self.assertRaises(AttributeError):
            wapi.invalid(12345)

    def test_invalid_response_format(self):
        with self.assertRaises(ValueError):
            api.API("key", resp_format="invalid")

    @responses.activate
    def test_lang(self):
        uri = "http://api.wunderground.com/api/key/alerts/lang:FR/q/12345.json"
        wapi = api.API("key", lang="FR")
        resp = {
            "response": {},
            "alerts": [],
        }
        responses.add(responses.GET, uri, json=resp)
        self.assertEqual(wapi.alerts(12345), resp)

    @responses.activate
    def test_conditions(self):
        uri = "http://api.wunderground.com/api/key/conditions/lang:EN/pws:1/q/12345.json"
        wapi = api.API("key")
        resp = {
            "response": {},
            "conditions": {
                "key": "value",
            },
        }
        responses.add(responses.GET, uri, json=resp)
        self.assertEqual(wapi.conditions(12345), resp)
        uri = "http://api.wunderground.com/api/key/conditions/lang:EN/pws:0/q/12345.json"
        wapi = api.API("key")
        resp = {
            "response": {},
            "conditions": {
                "key": "value",
            },
        }
        responses.add(responses.GET, uri, json=resp)
        self.assertEqual(wapi.conditions(12345, use_pws=False), resp)

    @responses.activate
    def test_forecast(self):
        uri = "http://api.wunderground.com/api/key/forecast/bestfct:1/lang:EN/q/12345.json"
        wapi = api.API("key")
        resp = {
            "response": {},
            "conditions": {
                "key": "value",
            },
        }
        responses.add(responses.GET, uri, json=resp)
        self.assertEqual(wapi.forecast(12345), resp)
        uri = "http://api.wunderground.com/api/key/forecast/bestfct:0/lang:EN/q/12345.json"
        responses.add(responses.GET, uri, json=resp)
        self.assertEqual(wapi.forecast(12345, use_bestfct=False), resp)

    @responses.activate
    def test_forecast10day(self):
        uri = "http://api.wunderground.com/api/key/forecast10day/bestfct:1/lang:EN/q/12345.json"
        wapi = api.API("key")
        resp = {
            "response": {},
            "conditions": {
                "key": "value",
            },
        }
        responses.add(responses.GET, uri, json=resp)
        self.assertEqual(wapi.forecast10day(12345), resp)
        uri = "http://api.wunderground.com/api/key/forecast10day/bestfct:0/lang:EN/q/12345.json"
        responses.add(responses.GET, uri, json=resp)
        self.assertEqual(wapi.forecast10day(12345, use_bestfct=False), resp)
