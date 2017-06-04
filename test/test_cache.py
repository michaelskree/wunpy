from unittest import TestCase
from wunpy import cache


class CacheTest(TestCase):

    def test_set(self):
        c = cache.Cache()
        c.set("key", "value")
        self.assertEqual(c.get("key"), "value")

    def test_get_uncached(self):
        c = cache.Cache()
        self.assertEqual(c.get("key"), None)

    def test_cache_timeout(self):
        c = cache.Cache(timeout=0)
        c.set("key", "value")
        self.assertEqual(c.get("key"), None)
