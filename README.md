# Django Slices Starter

This is a starter template for building django applications by organizing code into vertically integrated components called `slices`

## Requirements

The project uses python 3.13 and above

Dependencies for this project are managed by [uv][uv]

## Setup

Clone the project with git

```shell
git clone git@github.com:crisamunga/django-slices-starter.git
```

Setup an environment with uv

```shell
uv venv -p 3.13
```

Source the environment

```shell
source ./venv/bin/activate
```

Install all dependencies

```shell
uv sync
```

Setup secrets

```shell
cp .env.template .env
```

Update the created .env file and source it

```shell
set -a; source .env; set +a;
```

""" TIP

    To simplify this, you can append this to the .venv/bin/activate file so that your env variables are set up every time you activate the environment.

    Or alternatively you can use a tool like [mise](mise) or [direnv](direnv) to automatically source these environment variables when entering the directory.

You can now run the project

```shell
cd src/
./manage.py runserver
```

## Ecosystem

Type checking in the project is done using [Mypy][mypy]

Linting and formatting is done using [Ruff][ruff]

Testing is done using [Pytest][pytest]

Debug time profiling is done with [Django debug toolbar][ddt]

Background tasks are executed with [Restate][restate]

Telemetry (Profiling, Tracing, Metrics) is done using [Open Telemetry][otel]


## Project Structure

At the top level, this project is organized into this structure:

```tree
. # Holds base project configurations
|-- config # Holds the settings and common files for the project
|-- core # Holds the main application logic for the project
|-- docs # Holds project documentation
|-- infra # Holds the infrastracture needed to deploy this project
|-- lib # Holds helpers/tools that are re-used across apps/slices
|-- locale # Holds text translations
|-- logs # Holds log files. These are not committed to git, but the directory is kept empty to always be available
|-- schemas # Holds graphql and rest api schemas. These are also not committed to git, but once auto-generated are stored here.
|-- templates # Holds text and html templates, mostly used for email messages.
`-- tools # Holds cli commands and other utilities used in the project, mostly used during development / automated operations
```

## Creating slices

There is a helper command for scaffolding slices: `./manage.py startslice <app> <slice>` where app is the app name (usually `core`) and `slice` is the
name of the slice usually in singular form (e.g. `post`). This scaffolds a lot of the boilerplate for slices, but still needs their APIs to be registered
in the main app's `graphql.py`, `rest.py` and `models.py` files.

You can read the [guidelines](guidelines) for more guidance on how to author various components of a slice.

[otel]: https://opentelemetry.io/docs/languages/python/
[ddt]: https://django-debug-toolbar.readthedocs.io/en/latest/
[mypy]: https://mypy-lang.org/
[pytest]: https://docs.pytest.org/en/stable/
[ruff]: https://docs.astral.sh/ruff/
[uv]: https://docs.astral.sh/uv/
[restate]: https://docs.restate.dev/
[guidelines]: ./docs/guidelines/README.md
