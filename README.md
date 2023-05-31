[![CI](https://github.com/AndyHoang/nye_cache_py/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/AndyHoang/nye_cache_py/actions/workflows/main.yml)
[![Test Pypi](https://github.com/AndyHoang/nye_cache_py/actions/workflows/publish.yml/badge.svg?event=release)](https://github.com/AndyHoang/nye_cache_py/actions/workflows/publish.yml)

# Python Caching Library


This is a Python caching library, added small extension for [cachetools](https://github.com/tkem/cachetools)

## Features

Extend the [TTLCache](https://cachetools.readthedocs.io/en/latest/index.html?highlight=cache#cachetools.TTLCache)

* Once an item reach it TTL, mark it as expired, the outer function will try to trigger fetch new data. If the call get exception, reuse the staled content

## Installation

WIP

Install the library using pip:

```
pip install -i https://test.pypi.org/simple/ nye-cache-py==0.1.0
```

## Usage

TODO


## Milestones

This project has several milestones that need to be accomplished. These include:


### Version 0.1.x

- [x] Interface similar with TTLCache
- [X] Reuse cache if one expected exception happened when calling the main function
- [x] Install with pip using test pypi repo
- [x] Run CI/CD action in github
- [x] Integrate auto bump version command

###  Version 0.2.x

- [ ] Support expect multi exception at same time
- [ ] Improve unittest to ensure staled data will be removed if fresh data come
- [ ] Improve unittest by not using sleep to wait for cache expire
- [ ] Staled data should obey max size logic too


To track the progress of these milestones, you can view them on the [project's Milestones page](https://github.com/AndyHoang/nye_cache_py/milestones).

## Versioning

To keep track of changes made to the project and make it easier to keep the version in sync, we recommend using [Commitizen](https://commitizen-tools.github.io/commitizen/) within this project.

Commitizen provides an interactive prompt that allows contributors to follow a standardized format for commit messages, called conventional commits. By following this format, it's easier to understand the changes made to the project, and automate publish/release processes.

To use Commitizen to bump the version:

1. Stage your changes with `git add`, then run the `poetry run cz c` command instead of `git commit`. This command will open an interactive prompt that walks you through the process of crafting a commit message in the conventional format.
> You can use git commit without cz, but you need to obey the commit msg format convention

2. Push your changes (including the updated version number) to the repository with:

   ```
   poetry run cz bump -pr alpha
   ```

   ```
   poetry run cz bump --increment PATCH
   ```
3. Push the tag/branch to origin

4. Release
    TODO

## Contributing

- Fork the repository
- Create a new branch for your feature
- Make your changes and test them thoroughly
- Submit a pull request

## License

This project is licensed under the terms of the [MIT license](https://opensource.org/licenses/MIT).
