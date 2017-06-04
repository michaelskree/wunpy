wunpy: Python wrapper for the Weather Underground API
================================================
## Description
wunpy is a lightweight, Python wrapper around the Weather Underground API. Highlights include:
- Support for all API [data features][API data features]
- JSON and XML responses
- Optional in-memory caching of responses
## Usage
The following examples show how to use wunpy to retrieve data from the API:
```python
from wunpy.api import API

# Response format is controlled via the resp_format parameter (default: "json")
wapi = API("Insert API Key Here", resp_format="xml")
# Zipcode
conditions = wapi.conditions(55408)
# US state/city
forecast = wapi.forecast("MN/Minneapolis")
# Country/city
geolookup = wapi.geolookup("Australia/Sydney")
# Combine multiple API features
data = wapi.get(["conditions", "forecast"], 55408)
```
Each API feature can be accessed via a method with the same name. Most feature methods accept a query string that gets passed directly to the API. One exception is the ```history``` method, which accepts an additional ```date``` parameter.
```python
import datetime
from wunpy.api import API

wapi = API("Insert API Key Here")
history = wapi.history(55408, datetime.date(2017, 1, 1))
```
## Response Caching
API responses can be cached in memory for a certain amount of time.
```python
from wunpy.api import API
from wunpy.cache import Cache

# Specify cache timeout in seconds (default: 60)
wapi = API("Insert API Key Here", cache=Cache(timeout=30))
# Subsequent API calls will use cache by default. This behavior can be
# overridden by explicitly setting the use_cache parameter
conditions = wapi.conditions(55408, use_cache=False)
```
[API data features]: https://www.wunderground.com/weather/api/d/docs?d=data/index
