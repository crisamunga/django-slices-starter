import argparse
import os
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from typing import Any

from django.apps import apps
from django.core.management.templates import TemplateCommand


class Command(TemplateCommand):
    help = """
    Scaffolds a slice in an app. It creates this basic boilerplate:

        - errors.py - contains custom error classes
        - models.py - contains the django model(s), manager(s), and custom queryset classes(s)
        - rest.py - contains the REST API
        - graphql.py - contains the GraphQL API
        - services.py - contains the services, shared by all APIs
        - permissions.py - contains the permissions
        - validators.py - contains the input validators

    It accepts these arguments:

        app (str) : app where the slice should be created
        name (str) : name of the slice to create
        --files, -f (list[str]) : Comma-separated list of file names to add to the slice. If not provided, all files will be created.
        --exclude, -x (str) : directory name(s) to exclude, in addition to .git and __pycache__. Can be used multiple times.

"""  # noqa: E501

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("app", type=str, help="App where the slice should be created")
        parser.add_argument("name", type=str, help="Name of the slice to create")
        parser.add_argument(
            "--files",
            "-f",
            dest="files",
            action="append",
            default=[],
            help="The file name(s) to render. Separate multiple file names with commas, or use -f multiple times.",
        )
        parser.add_argument(
            "--exclude",
            "-x",
            action="append",
            default=argparse.SUPPRESS,
            nargs="?",
            const="",
            help=("The directory name(s) to exclude, in addition to .git and __pycache__. Can be used multiple times."),
        )
        parser.formatter_class = RawTextHelpFormatter

    def handle(self, *args: Any, **options: Any) -> None:
        app_name = options.pop("app")
        app_path = apps.get_app_config(app_name).path
        name = options.pop("name")
        resource_name_plural: str = f"{name.lower()}s" if not name.lower().endswith("s") else name.lower()
        target = Path(app_path) / resource_name_plural
        options["directory"] = str(target) if not options.get("directory") else options["directory"]
        template_dir = Path(apps.get_app_config("slices").path) / "management" / "templates" / "slice"
        options["template"] = str(template_dir)
        options["extensions"] = ["py"]

        target.mkdir(parents=True, exist_ok=True)

        super().handle("app", name, target, **options)

        os.system(f"ruff format {target}")  # noqa: S605 # auto-format the generated code
        os.system(f"ruff check {target} --fix")  # noqa: S605 # auto-fix linting issues
