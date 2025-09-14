# Django Slices Starter

This is a starter template for building django applications using the the vertical slices architecture

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
|-- docs # Holds project documentation
|-- infra # Holds the infrastracture needed to deploy this project
|-- scripts # Holds the bash scripts used in the project
`-- src # Holds the actual django project
  |-- config # Holds the settings and common files for the project
  |-- core # Holds the main application logic for the project
  `-- lib # Holds helpers/tools that are re-used across apps/slices
```

## Creating slices

There is a helper command for creating slices.

## Quirks

Some aspects of django do not feat neatly into the slices way of doing things since django expects certain files to be in specific folders. These include:

- Templates. There is no easy way to have each slice hold it's own templates.
- Models: We can define models in the slices, but these have to be imported in the app level models.py file
- Django commands: Django commands are automatically discovered from the management/commands folder, and cannot be in the individual slices.

## Benefits

Despite the quirks mentioned above, there are still benefits to using this structure. To list a few:

- Locality of behavior. Most of what you need to work with a resource/feature is localized hence easy to make changes while being aware of what side effects there will be.
- Simplicity. This project structure is easy to wrap your head around, regardless of the project size. It's also really easy to make decisions like where to add features, or where a feature is located.
- Evolution. It evolves well as the business behind the application evolves. It's more immune to domain boundary shifts.
- Migration. In the event any of the libraries in the project stops being maintained (except Django of course), this structure makes it possible to use the strangler-fig pattern for a piece by piece migration. A similar approach can be used if there is a need to pull out some features / slices to be written in different languages / using different tools.
- Performance. Especially for graphql which is susceptible to N+1 queries, this structure naturally eliminates N+1 queries.
- Monitoring. This structure makes it easy to track performance of the application at a slice/feature level.


[otel]: https://opentelemetry.io/docs/languages/python/
[ddt]: https://django-debug-toolbar.readthedocs.io/en/latest/
[mypy]: https://mypy-lang.org/
[pytest]: https://docs.pytest.org/en/stable/
[ruff]: https://docs.astral.sh/ruff/
[uv]: https://docs.astral.sh/uv/
[restate]: https://docs.restate.dev/
