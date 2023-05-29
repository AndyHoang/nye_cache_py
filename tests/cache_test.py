import os
import time

import pytest

from unittest.mock import Mock
from os.path import abspath, curdir
from os.path import join as join_path

from nye_cache import cached, NYECache
from cachetools import Cache



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
    def this_is_a_function() -> int:

        with open(FILE_PATH, 'a') as f:
            f.write(CONTENT)

        return 1

    result = this_is_a_function()

    assert this_is_a_function() == result

    with open(FILE_PATH, 'r') as f:
        file_content = f.read()

    assert file_content == CONTENT

    clean()

def test_put_expired_cache_back_in_when_func_exception() -> None:
    _this_is_an_internal_function = Mock(side_effect=[1, 0, 0, 0, 2, 1])

    my_cache = NYECache(ttl=2, maxsize=256, timer=time.time)
    @cached(cache=my_cache, info=True, exc=MyException)
    def this_is_a_function(a, b):
        value = _this_is_an_internal_function()
        if value == 0:
            raise MyException("This is a custom exception")
        return value

    val = this_is_a_function(1, 2)  # Normal first run
    assert val == 1
    assert this_is_a_function.cache_info().hits == 0
    val = this_is_a_function(1, 2)  # Normal sencond run
    assert val == 1
    assert this_is_a_function.cache_info().hits == 1

    time.sleep(3)
    # cache is expired
    _ = this_is_a_function(1, 2) # side_effect return 0 keep cache
    _ = this_is_a_function(1, 2) # side_effect call has exception keep cache
    val = this_is_a_function(1, 2) # side_effect return 2

    print(this_is_a_function.cache_info())
    assert this_is_a_function.cache_info().misses == 2
    assert this_is_a_function.cache_info().hits == 3

    assert val == 2
    with pytest.raises(MyException):
        this_is_a_function(3, 1)  # Exception should happens here
