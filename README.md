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

## Contributing

- Fork the repository
- Create a new branch for your feature
- Make your changes and test them thoroughly
- Submit a pull request

## License

This project is licensed under the terms of the [MIT license](https://opensource.org/licenses/MIT).
