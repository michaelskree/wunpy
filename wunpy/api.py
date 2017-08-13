import requests
from xml.etree import ElementTree

uri_base = 'http://api.wunderground.com/api'


class API(object):
    """Wrapper for the wunderground.com weather API."""

    def __init__(self, api_key, resp_format="json", lang="EN", cache=None):
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
        self.lang = lang
        self.cache = cache
        self.features = [
            "alerts",
            "almanac",
            "astronomy",
            "geolookup",
            "hourly",
            "hourly10day",
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

    def _build_uri(self, features, tail, settings=None):
        """Build the request URI.

        Build the full request URI. This includes the API key, feature string,
        and query string.

        :param features: List of API features.
        :param tail: Final URI component. Typically a query string.
        :param settings: Query settings.
        """
        if settings is None:
            settings = {}

        settings = {"lang": self.lang, **settings}
        s = "/".join("{}:{}".format(k, settings[k]) for k in sorted(settings))

        components = [uri_base, self.api_key, *features, s, tail]

        return "/".join(components) + ".{}".format(self.resp_format)

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

    def _get(self, uri, use_cache=True):
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

    def get(self, features, query, settings=None, use_cache=True):
        """Get multiple API features for a specific query string.

        :param features: List of API features to get.
        :param query: The query string to use.
        :param settings: Query settings.
        :param use_cache: Whether or not to use the API cache.
        """
        tail = "q/{}".format(str(query))
        uri = self._build_uri(features, tail, settings)

        return self._get(uri, use_cache=use_cache)

    def current_hurricane(self, use_cache=True):
        """Get current hurricane information.

        Get current hurricane information. This feature doesn't accept a query
        string.

        :param use_cache: Whether or not to use the API cache.
        """
        uri = self._build_uri(["currenthurricane"], "view")

        return self._get(uri, use_cache=use_cache)

    def history(self, query, history_date, use_cache=True):
        """Get historical weather data.

        Get historical weather data for a specific location and date.

        :param query: The query string to use.
        :param history_date: The date to use.
        """

        feature = "history_{}".format(history_date.strftime("%Y%m%d"))

        return self.get([feature], query, use_cache=use_cache)

    def conditions(self, query, use_pws=True, use_cache=True):
        """Get current conditions.

        :param query: The query string to use.
        :param use_pws: Whether or not to use personal weather stations.
        :param use_cache: Whether or not to use the API cache.
        """
        settings = {"pws": int(use_pws)}

        return self.get(
            ["conditions"],
            query,
            settings=settings,
            use_cache=use_cache
        )

    def forecast(self, query, use_bestfct=True, use_cache=True):
        """Get weather forecast.

        :param query: The query string to use.
        :param use_bestfct: Whether or not to use Weather Underground Best
                            Forecast.
        :param use_cache: Whether or not to use the API cache.
        """
        settings = {"bestfct": int(use_bestfct)}

        return self.get(
            ["forecast"],
            query,
            settings=settings,
            use_cache=use_cache
        )

    def forecast10day(self, query, use_bestfct=True, use_cache=True):
        """Get weather forecast for the next 10 days.

        :param query: The query string to use.
        :param use_bestfct: Whether or not to use Weather Underground Best
                            Forecast.
        :param use_cache: Whether or not to use the API cache.
        """
        settings = {"bestfct": int(use_bestfct)}

        return self.get(
            ["forecast10day"],
            query,
            settings=settings,
            use_cache=use_cache
        )


class APIError(Exception):
    """Raised when API returns an error."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
