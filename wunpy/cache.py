import time


class Cache(object):
    """Simple memory-based cache for API responses"""

    def __init__(self, timeout=60):
        """Construct new cache object.

        :param timeout: Cache timeout in seconds.
        """
        self.timeout = timeout
        self.entries = {}

    def set(self, key, value):
        """Store item in cache.

        :param key: Item key.
        :param value: Item value
        """
        self.entries[key] = {
            "time": time.time(),
            "value": value,
        }

    def get(self, key):
        """Get item from cache.

        :param key: Item key
        """
        entry = self.entries.get(key)

        if entry:
            if entry["time"] + self.timeout > time.time():
                return entry["value"]
            del self.entries[key]

        return None
