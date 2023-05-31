__version__ = "0.1.1a0"

__all__ = (
    "NYECache",
    "cached",
)

import logging
import functools
import collections
from cachetools import Cache, _CacheInfo, TTLCache, keys
import time

logger = logging.getLogger(__name__)

# class StaledCacheError(Exception):
    # def __init__(self, key, value):
        # self.key = key
        # self.value = value
        # super().__init__(self, "StaledCacheError: key: %s, value: %s" % (self.key, self.value))

    # def __str__(self):
        # return "StaledCacheError: key: %s, value: %s" % (self.key, self.value)

class NYECache(TTLCache):
    """NYECache
    Not yet expired cache!
    Extended from TTLCache
    it will remove everything but actual content in __data
    It still obey the maxsize rules
    """

    _staled_data = dict()

    def __init__(self, maxsize, ttl, timer=time.monotonic, getsizeof=None):
        super().__init__(maxsize, ttl, timer=timer, getsizeof=getsizeof)

    def posibility_staled_get_item(self, key):
        """
        shortcut method getting cached data without the hassle of timer
        this can raised KeyError of course
        :param key:
        """
        logger.warning(f"posibility_staled_get_item: {key}")
        return self._staled_data[key]

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        try:
            del self._staled_data[key]
        except KeyError:
            pass

    def expire(self, time=None):
        """similiar with def expired,
        """
        if time is None:
            time = self.timer()
        root = self._TTLCache__root
        curr = root.next
        links = self._TTLCache__links
        cache_delitem = Cache.__delitem__
        while curr is not root and not (time < curr.expires):
            try:
                self._staled_data[curr.key] = Cache.__getitem__(self, curr.key)
            except KeyError:
                pass
            cache_delitem(self, curr.key)
            del links[curr.key]
            next = curr.next
            curr.unlink()
            curr = next

def cached(cache, key=keys.hashkey, lock=None, info=False, exc=Exception):
    """Decorator to wrap a function with a memoizing callable that saves
    results in a cache.

    """

    def decorator(func):

        def nye_func(*args, **kwargs):
            k = key(*args, **kwargs)
            try:
                return (func(*args, **kwargs), None)
            except exc as er:
                logger.info(f"{func.__name__}({args}, {kwargs}) raised {exc.__name__}}} getting exception, try to use staled cache of key {k}")
                try:
                    return cache.posibility_staled_get_item(k), er
                except KeyError:
                    raise er

        if info:
            hits = misses = 0

            if isinstance(cache, Cache):

                def getinfo():
                    nonlocal hits, misses
                    return _CacheInfo(hits, misses, cache.maxsize, cache.currsize)

            elif isinstance(cache, collections.abc.Mapping):

                def getinfo():
                    nonlocal hits, misses
                    return _CacheInfo(hits, misses, None, len(cache))

            else:

                def getinfo():
                    nonlocal hits, misses
                    return _CacheInfo(hits, misses, 0, 0)

            if cache is None:

                def wrapper(*args, **kwargs):
                    nonlocal misses
                    misses += 1
                    v, _ = nye_func(*args, **kwargs)
                    return v

                def cache_clear():
                    nonlocal hits, misses
                    hits = misses = 0

                cache_info = getinfo

            elif lock is None:

                def wrapper(*args, **kwargs):
                    nonlocal hits, misses
                    k = key(*args, **kwargs)
                    try:
                        result = cache[k]
                        hits += 1
                        return result
                    except KeyError:
                        misses += 1
                    v, err = nye_func(*args, **kwargs)
                    try:
                        if err is None:
                            cache[k] = v
                    except ValueError:
                        pass  # value too large
                    return v

                def cache_clear():
                    nonlocal hits, misses
                    cache.clear()
                    hits = misses = 0

                cache_info = getinfo

            else:

                def wrapper(*args, **kwargs):
                    nonlocal hits, misses
                    k = key(*args, **kwargs)
                    try:
                        with lock:
                            result = cache[k]
                            hits += 1
                            return result
                    except KeyError:
                        with lock:
                            misses += 1
                    v, err = nye_func(*args, **kwargs)
                    # in case of a race, prefer the item already in the cache
                    try:
                        with lock:
                            if err is None:
                                return cache.setdefault(k, v)
                    except ValueError:
                        return v  # value too large

                def cache_clear():
                    nonlocal hits, misses
                    with lock:
                        cache.clear()
                        hits = misses = 0

                def cache_info():
                    with lock:
                        return getinfo()

        else:
            if cache is None:

                def wrapper(*args, **kwargs):
                    v, _ = nye_func(*args, **kwargs)
                    return v
                def cache_clear():
                    pass

            elif lock is None:

                def wrapper(*args, **kwargs):
                    k = key(*args, **kwargs)
                    try:
                        return cache[k]
                    except KeyError:
                        pass  # key not found
                    v, err = nye_func(*args, **kwargs)
                    try:
                        if err is None:
                            cache[k] = v
                    except ValueError:
                        pass  # value too large
                    return v

                def cache_clear():
                    cache.clear()

            else:

                def wrapper(*args, **kwargs):
                    k = key(*args, **kwargs)
                    try:
                        with lock:
                            return cache[k]
                    except KeyError:
                        pass  # key not found
                    v, err = nye_func(*args, **kwargs)
                    # in case of a race, prefer the item already in the cache
                    try:
                        with lock:
                            if err is None:
                                return cache.setdefault(k, v)
                    except ValueError:
                        return v  # value too large

                def cache_clear():
                    with lock:
                        cache.clear()

            cache_info = None

        wrapper.cache = cache
        wrapper.cache_key = key
        wrapper.cache_lock = lock
        wrapper.cache_clear = cache_clear
        wrapper.cache_info = cache_info

        return functools.update_wrapper(wrapper, func)

    return decorator

