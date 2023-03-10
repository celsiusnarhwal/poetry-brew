# poetry-brew

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/poetry-brew?logo=python&logoColor=white&style=for-the-badge)](https://pypi.org/project/poetry-brew)
[![PyPI](https://img.shields.io/pypi/v/poetry-brew?logo=pypi&color=green&logoColor=white&style=for-the-badge)](https://pypi.org/project/poetry-brew)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/celsiusnarhwal/poetry-brew?logo=github&color=orange&logoColor=white&style=for-the-badge)](https://github.com/celsiusnarhwal/poetry-brew/releases)
[![PyPI - License](https://img.shields.io/pypi/l/poetry-brew?color=03cb98&style=for-the-badge)](https://github.com/celsiusnarhwal/poetry-brew/blob/main/LICENSE.md)

poetry-brew is a [Poetry](https://python-poetry.org/) plugin that generates Homebrew formulae for Poetry projects.

## Installation

```bash
poetry self add poetry-brew
```
## Requirements

poetry-brew can only generate formulae for packages that meet the following criteria:

- The package must be published on PyPI.
- `pyproject.toml` and `poetry.lock` must be present in the directory where `poetry brew` is run.
- `pyproject.toml` must specify values for `tool.poetry.name`, `tool.poetry.version`,
  and `tool.poetry.dependencies.python`.
    - `tool.poetry.name` must be a case-insensitive match with the package's name on PyPI.
    - `tool.poetry.version` must match a version of the package that has been published on PyPI.
     For full usage information, run `poetry brew --help`.

## Usage

```bash
poetry brew
```

`poetry brew` supports the `--with`, `--without`, and `--only` options, which function identically to `poetry install`.
For full usage information, run `poetry brew --help`.

## Configuration

poetry-brew can be configured through a `tool.brew.config` section in `pyproject.toml`.

```toml
[tool.brew.config]
dependencies = []
```

### Supported Options

- `dependencies` (`list`, default: `[]`): A list of other Homebrew formulae the package depends on.

## License

poetry-brew is licensed under the [MIT License](https://github.com/celsiusnarhwal/poetry-brew/blob/main/LICENSE.md).
