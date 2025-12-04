# This file is used for a set of commands to manage Graphql and Hive-related tasks.
# It makes a few assumptions about the project, specifically that:
# - The project has a single Django app named "core". All slices are placed in this core app
# - Each slice with Graphql schemas has a "graphql" package / module inside it, with a schema object
# - The Hive CLI is installed and available in the environment where this command is run
# - Care should be taken to ensure that the Hive CLI is what's actually available as `hive` in the environment
# Hive CLI reference: https://the-guild.dev/graphql/hive/docs/api-reference/cli

import os
from pathlib import Path
from typing import Annotated

from django.conf import settings
from django_typer.management import Typer
from rich import print
from typer import Option

from config.graphql import api

schema_dir: Path = settings.BASE_DIR / "schemas"

app = Typer(
    name="hive",
    help="Wrapper around Hive CLI.",
)  # type: ignore # TODO: Add missing generic type params


@app.command(name="export")
def export() -> None:
    """Export graphql schemas from all slices."""
    for endpoint in api.endpoints:
        print(f"Exporting schema for endpoint: [bold]{endpoint.name}[/bold]")
        schema_name = f"{endpoint.name.replace('/', '_')}.graphql"
        schema_path = schema_dir / schema_name
        with schema_path.open("w") as f:
            f.write(endpoint.schema.as_str())


@app.command(name="publish")
def publish(
    *,
    access_token: Annotated[
        str | None,
        Option(
            "--access-token",
            help="Hive registry access token. If empty, uses the HIVE_REGISTRY_ACCESS_TOKEN environment variable",
        ),
    ] = None,
    target: Annotated[
        str | None,
        Option(
            "--target",
            help="Hive target (usually the release stage). If empty, defaults to the HIVE_TARGET environment variable",
        ),
    ] = "federation",
) -> None:
    """Publish schemas to Hive registry."""
    access_token = access_token or os.getenv("HIVE_REGISTRY_ACCESS_TOKEN")
    if not access_token:
        print(
            "[red]Error:[/red] Hive registry access token is required. Provide it via [bold]--access-token[/bold] or [bold]HIVE_REGISTRY_ACCESS_TOKEN[/bold] environment variable."  # noqa: E501
        )
        return

    target = target or os.getenv("HIVE_TARGET", "federation")
    if not target:
        print(
            "[red]Error:[/red] Hive target is required. Provide it via [bold]--target[/bold] or [bold]HIVE_TARGET[/bold] environment variable."  # noqa: E501
        )
        return

    command = "hive schema:publish --registry.accessToken {access_token} --target {target} --service {service} --url {url} {file}"  # noqa: E501
    for endpoint in api.endpoints:
        print(f"Publishing schema for endpoint: [bold]{endpoint.name}[/bold]")
        schema_name = f"{endpoint.name.replace('/', '_')}.graphql"
        schema_path = schema_dir / schema_name
        if not schema_path.exists():
            print(f"[yellow]Warning:[/yellow] Schema file {schema_path} does not exist. Skipping.")
            continue

        filled_command = command.format(
            access_token=access_token,
            target=target,
            service=endpoint.name,
            url=f"{settings.APP_URL}/graphql/" + endpoint.path,
            file=schema_path,
        )
        result = os.system(filled_command)  # noqa: S605
        if result != 0:
            print(f"[red]Error:[/red] Schema publish failed for endpoint: [bold]{endpoint.name}[/bold]")
        else:
            print(f"[green]Success:[/green] Schema published for endpoint: [bold]{endpoint.name}[/bold]")


@app.command(name="check")
def check(
    *,
    access_token: Annotated[
        str | None,
        Option(
            "--access-token",
            help="Hive registry access token. If empty, uses the HIVE_REGISTRY_ACCESS_TOKEN environment variable",
        ),
    ] = None,
    target: Annotated[
        str | None,
        Option(
            "--target",
            help="Hive target (usually the release stage). If empty, defaults to the HIVE_TARGET environment variable",
        ),
    ] = "federation",
) -> None:
    """Check if schemas are valid and compliant with gql guidelines."""
    access_token = access_token or os.getenv("HIVE_REGISTRY_ACCESS_TOKEN")
    if not access_token:
        print(
            "[red]Error:[/red] Hive registry access token is required. Provide it via [bold]--access-token[/bold] or [bold]HIVE_REGISTRY_ACCESS_TOKEN[/bold] environment variable."  # noqa: E501
        )
        return

    target = target or os.getenv("HIVE_TARGET", "federation")
    if not target:
        print(
            "[red]Error:[/red] Hive target is required. Provide it via [bold]--target[/bold] or [bold]HIVE_TARGET[/bold] environment variable."  # noqa: E501
        )
        return

    command = "hive schema:check --registry.accessToken {access_token} --target {target} --service {service} --url {url} {file}"  # noqa: E501

    result: int = 0

    for endpoint in api.endpoints:
        print(f"Checking schema for endpoint: [bold]{endpoint.name}[/bold]")
        schema_name = f"{endpoint.name.replace('/', '_')}.graphql"
        schema_path = schema_dir / schema_name
        if not schema_path.exists():
            print(f"[yellow]Warning:[/yellow] Schema file {schema_path} does not exist. Skipping.")
            continue

        filled_command = command.format(
            access_token=access_token,
            target=target,
            service=endpoint.name,
            url=f"{settings.APP_URL}/graphql/" + endpoint.path,
            file=schema_path,
        )
        endpoint_result = os.system(filled_command)  # noqa: S605
        if result != 0:
            print(f"[red]Error:[/red] Schema check failed for endpoint: [bold]{endpoint.name}[/bold]")
        else:
            print(f"[green]Success:[/green] Schema check passed for endpoint: [bold]{endpoint.name}[/bold]")
        result += endpoint_result

    if result != 0:
        print("[red]One or more schema checks failed.[/red]")
        raise SystemExit(1)


@app.command(name="delete")
def delete(
    service_name: Annotated[str, Option(help="Name of the service whose schema should be deleted from Hive registry")],
    *,
    access_token: Annotated[
        str | None,
        Option(
            "--access-token",
            help="Hive registry access token. If empty, uses the HIVE_REGISTRY_ACCESS_TOKEN environment variable",
        ),
    ] = None,
    target: Annotated[
        str | None,
        Option(
            "--target",
            help="Hive target (usually the release stage). If empty, defaults to the HIVE_TARGET environment variable",
        ),
    ] = "federation",
) -> None:
    """Delete schemas from Hive registry."""
    access_token = access_token or os.getenv("HIVE_REGISTRY_ACCESS_TOKEN")
    if not access_token:
        print(
            "[red]Error:[/red] Hive registry access token is required. Provide it via [bold]--access-token[/bold] or [bold]HIVE_REGISTRY_ACCESS_TOKEN[/bold] environment variable."  # noqa: E501
        )
        return

    target = target or os.getenv("HIVE_TARGET", "federation")
    if not target:
        print(
            "[red]Error:[/red] Hive target is required. Provide it via [bold]--target[/bold] or [bold]HIVE_TARGET[/bold] environment variable."  # noqa: E501
        )
        return

    command = "hive schema:delete --registry.accessToken {access_token} --target {target} {service}"
    filled_command = command.format(
        access_token=access_token,
        target=target,
        service=service_name,
    )
    result = os.system(filled_command)  # noqa: S605
    if result != 0:
        print(f"[red]Error:[/red] Schema delete failed for service: [bold]{service_name}[/bold]")
    else:
        print(f"[green]Success:[/green] Schema deleted for service: [bold]{service_name}[/bold]")
