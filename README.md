# Python Caching Library

This is a Python caching library and a small extension of [cachetools](https://github.com/tkem/cachetools), a popular Python caching library.

## Features

Extend the [TTLCache](https://cachetools.readthedocs.io/en/latest/index.html?highlight=cache#cachetools.TTLCache)

* Once an item reach it TTL, mark it as expired, the outer function will try to trigger fetch new data. If the call get exception, reuse the staled content

## Installation

Install the library using pip:

```
pip install nye-cache-py
```

## Usage

TODO


## Milestones

This project has several milestones that need to be accomplished. These include:


### Version 0.1.x

- [x] Interface similar with TTLCache
- [X] Reuse cache if one expected exception happened when calling the main function
- [ ] Install with pip using test pypi repo
- [ ] Support expect multi exception
- [ ] Improve unittest to ensure staled data will be removed if fresh data come

###  Version 0.2.x

- [ ] Improve unittest by not using sleep to wait for cache expire
- [ ] Staled data should obey max size logic too


To track the progress of these milestones, you can view them on the [project's Milestones page](https://github.com/AndyHoang/nye_cache_py/milestones).

## Contributing

- Fork the repository
- Create a new branch for your feature
- Make your changes and test them thoroughly
- Submit a pull request

## License

This project is licensed under the terms of the [MIT license](https://opensource.org/licenses/MIT).
