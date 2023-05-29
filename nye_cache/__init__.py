__all__ = (
    "NYECache",
    "cached",
)

import logging
import functools
import collections
from cachetools import Cache, _CacheInfo, TTLCache, keys

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

    def posibility_staled_get_item(self, key):
        """
        shortcut method getting cached data without the hassle of timer
        this can raised KeyError of course
        :param key:
        """
        logger.info(f"posibility_staled_get_item: {key}")
        return Cache.__getitem__(self, key)


    # def __missing__(self, key):
        # try:
            # raise StaledCacheError(key, self.posibility_staled_get_item(key))
        # except KeyError:
            # raise

    def just_expire(self, time=None):
        """similiar with def expired,
        but do not remove the actual cache in __data[]
        """
        if time is None:
            time = self.timer()
        root = self.__root
        curr = root.next
        links = self.__links
        # cache_delitem = Cache.__delitem__
        while curr is not root and not (time < curr.expires):
            # cache_delitem(self, curr.key) # not remove here
            del links[curr.key]
            next = curr.next
            curr.unlink()
            curr = next

    def __repr__(self, cache_repr=Cache.__repr__):
        with self.__timer as time:
            self.just_expire(time)
            return cache_repr(self)


    def __len__(self, cache_len=Cache.__len__):
        with self.__timer as time:
            self.just_expire(time)
            return cache_len(self)

    def clear(self):
        with self.__timer as time:
            self.expire(time)
            Cache.clear(self)


    def __setstate__(self, state):
        self.__dict__.update(state)
        root = self.__root
        root.prev = root.next = root
        for link in sorted(self.__links.values(), key=lambda obj: obj.expires):
            link.next = root
            link.prev = prev = root.prev
            prev.next = root.prev = link
        self.expire(self.timer())

    def popitem(self):
        """Remove and return the `(key, value)` pair least recently used that
        has not already expired.
        """
        with self.timer as time:
            self.expire(time)
            try:
                key = next(iter(self.__links))
            except StopIteration:
                raise KeyError("%s is empty" % type(self).__name__) from None
            else:
                return (key, self.pop(key))

def cached(cache, key=keys.hashkey, lock=None, info=False, exc=Exception):
    """Decorator to wrap a function with a memoizing callable that saves
    results in a cache.

    """

    def decorator(func):

        def nye_func(*args, **kwargs):
            k = key(*args, **kwargs)
            try:
                return func(*args, **kwargs)
            except exc as er:
                logger.warning(f"{func.__name__}({args}, {kwargs}) raised {exc.__name__}}} getting exception, try to use staled cache of key {k}")
                try:
                    return cache.posibility_staled_get_item(k)
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
                    return nye_func(*args, **kwargs)

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
                    v = nye_func(*args, **kwargs)
                    try:
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
                    v = nye_func(*args, **kwargs)
                    # in case of a race, prefer the item already in the cache
                    try:
                        with lock:
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
                    return nye_func(*args, **kwargs)

                def cache_clear():
                    pass

            elif lock is None:

                def wrapper(*args, **kwargs):
                    k = key(*args, **kwargs)
                    try:
                        return cache[k]
                    except KeyError:
                        pass  # key not found
                    v = nye_func(*args, **kwargs)
                    try:
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
                    v = nye_func(*args, **kwargs)
                    # in case of a race, prefer the item already in the cache
                    try:
                        with lock:
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

