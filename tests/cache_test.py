import os
import time

import pytest

from os.path import abspath, curdir
from os.path import join as join_path

from nye_cache import cached, NYECache
from cachetools import Cache


from unittest.mock import MagicMock


FILE_NAME = '.test_cache.to_be_deleted'
FILE_PATH = abspath(join_path(curdir, FILE_NAME))
CONTENT = 'testing cached'


class MyException(Exception):
    pass

def clean() -> None:
    try:
        os.remove(FILE_PATH)
    except FileNotFoundError:
        pass


def test_can_use_cache() -> None:
    @cached(cache=Cache(maxsize=256))
    def cached_the_function() -> int:

        with open(FILE_PATH, 'a') as f:
            f.write(CONTENT)

        return 1

    result = cached_the_function()

    assert cached_the_function() == result

    with open(FILE_PATH, 'r') as f:
        file_content = f.read()

    assert file_content == CONTENT

    clean()

def test_put_expired_cache_back_in_when_func_exception() -> None:
    mock_method = MagicMock()

    my_cache = NYECache(ttl=2, maxsize=256, timer=time.time)

    @cached(cache=my_cache, info=True, exc=MyException)
    def cached_the_function(a, b):
        x = mock_method()
        return x

    mock_method.return_value = 1
    val = cached_the_function(1, 2)  # Normal first run
    assert val == 1
    assert cached_the_function.cache_info().hits == 0

    mock_method.side_effect = MyException("test")
    val = cached_the_function(1, 2)  # Normal sencond run because of cached
    assert val == 1
    assert cached_the_function.cache_info().hits == 1
    assert len(my_cache) == 1

    time.sleep(4)

    assert len(my_cache) == 0
    assert len(my_cache._staled_data) == 1

    val = cached_the_function(1, 2) # side_effect exception but we staled is keep
    assert val == 1

    mock_method.side_effect = Exception("bigger")

    with pytest.raises(Exception):
        cached_the_function(1, 2) # should have error
    assert len(my_cache._staled_data) == 1
