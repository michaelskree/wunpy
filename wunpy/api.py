import requests
from xml.etree import ElementTree

uri_base = 'http://api.wunderground.com/api'


class API(object):
    """Wrapper for the wunderground.com weather API."""

    def __init__(self, api_key, resp_format="json", cache=None):
        """Construct new API object.

        :param api_key: API key.
        :param resp_format: Response format (json or xml).
        :param cache: API cache.
        """
        self.api_key = api_key
        if resp_format in ["json", "xml"]:
            self.resp_format = resp_format
        else:
            raise ValueError("API response format must be 'json' or 'xml'")
        self.cache = cache
        self.features = [
            "alerts",
            "almanac",
            "astronomy",
            "conditions",
            "forecast",
            "forecast_10_day",
            "geolookup",
            "hourly",
            "hourly_10_day",
            "planner",
            "rawtide",
            "satellite",
            "tide",
            "webcams",
            "yesterday",
        ]

    def __getattr__(self, name):
        """Handle lookups of undefined attributes.

        This is used to implement a getter method for every API feature that
        doesn't require special parameter processing or a custom URI.

        :param name: Attribute name
        """
        if name in self.features:
            def get_feature(query, use_cache=True):
                return self.get([name], query, use_cache=use_cache)
            return get_feature
        raise AttributeError()

    def _build_uri_base(self, features):
        """Build the request URI base.

        Build the base of the request URI. This includes the API key and the
        feature string.

        :param features: List of API features.
        """
        feature_str = "/".join(features)

        return "{}/{}/{}".format(uri_base, self.api_key, feature_str)

    def _build_uri(self, features, query):
        """Build the request URI.

        Build the full request URI. This includes the API key, feature string,
        and query string.

        :param features: List of API features.
        :param query: The query string to use.
        """
        base = self._build_uri_base(features)

        return "{}/q/{}.{}".format(base, query, self.resp_format)

    def _request(self, uri):
        """Issue a request to the API.

        :param uri: Request URI.
        """
        resp = requests.get(uri)
        error_msg = None

        if self.resp_format == "json":
            data = resp.json()
            error = data["response"].get("error")

            if error:
                error_msg = error["description"]
        else:
            data = ElementTree.fromstring(resp.text)
            error = data.find("error")

            if error:
                error_msg = error.find("description").text

        if error_msg is not None:
            raise APIError(error_msg)

        return data

    def _get_api_data(self, uri, use_cache=True):
        """Get API data.

        Get data from cache or issue a request to the API.

        :param uri: Request URI.
        :param use_cache: Whether or not to use the API cache.
        """
        if use_cache and self.cache:
            results = self.cache.get(uri)

            if results:
                return results

        results = self._request(uri)

        if use_cache and self.cache:
            self.cache.set(uri, results)

        return results

    def get(self, features, query, use_cache=True):
        """Get multiple API features for a specific query string.

        :param features: List of API features to get.
        :param query: The query string to use.
        :param use_cache: Whether or not to use the API cache.
        """
        uri = self._build_uri(features, query)

        return self._get_api_data(uri, use_cache=use_cache)

    def current_hurricane(self, use_cache=True):
        """Get current hurricane information.

        Get current hurricane information. This feature doesn't accept a query
        string.

        :param use_cache: Whether or not to use the API cache.
        """
        base = self._build_uri_base(["currenthurricane"])
        uri = "{}/view.{}".format(base, self.resp_format)

        return self._get_api_data(uri, use_cache=use_cache)

    def history(self, query, history_date, use_cache=True):
        """Get historical weather data.

        Get historical weather data for a specific location and date.

        :param query: The query string to use.
        :param history_date: The date to use.
        """

        feature = "history_{}".format(history_date.strftime("%Y%m%d"))

        return self.get([feature], query, use_cache=use_cache)


class APIError(Exception):
    """Raised when API returns an error."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
