"""Command-line interface for interactive and scripted use."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from newbie_project_builder import __version__
from newbie_project_builder.app import Application
from newbie_project_builder.errors import BuilderError
from newbie_project_builder.models import ProjectKind, ProjectOptions, Visibility
from newbie_project_builder.project import slugify


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        prog="npb",
        description="Safety-first project setup for complete beginners.",
    )
    result.add_argument("--home", type=Path, help="Builder-owned logs and state folder")
    result.add_argument("--dry-run", action="store_true", help="Preview commands and files only")
    subcommands = result.add_subparsers(dest="command")
    subcommands.add_parser("menu", help="Open the guided menu")
    subcommands.add_parser("diagnose", help="Run read-only computer checks")
    subcommands.add_parser("setup", help="Run the guided prerequisite setup")
    subcommands.add_parser("integrations", help="Show Codex integration status")
    subcommands.add_parser("support-bundle", help="Create a sanitized support archive")
    subcommands.add_parser("latest-log", help="Print the newest log path")
    subcommands.add_parser("version", help="Print the program version")

    create = subcommands.add_parser("create", help="Create a project non-interactively")
    create.add_argument("--name", required=True)
    create.add_argument("--kind", choices=[item.value for item in ProjectKind], default="generic")
    create.add_argument("--audience", default="Only me")
    create.add_argument(
        "--visibility",
        choices=[item.value for item in Visibility],
        default="local-only",
    )
    create.add_argument("--parent", type=Path, required=True)
    create.add_argument("--description", default="")
    create.add_argument("--no-git", action="store_true")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    if arguments.command == "version":
        print(__version__)
        return 0
    app = Application(home=arguments.home, dry_run=arguments.dry_run)
    try:
        if arguments.command in {None, "menu"}:
            return app.menu()
        if arguments.command == "diagnose":
            app.banner()
            return app.diagnostics()
        if arguments.command == "setup":
            app.banner()
            return app.setup()
        if arguments.command == "integrations":
            app.banner()
            return app.show_integrations()
        if arguments.command == "support-bundle":
            return app.support_bundle()
        if arguments.command == "latest-log":
            return app.latest_log()
        if arguments.command == "create":
            options = ProjectOptions(
                arguments.name,
                slugify(arguments.name),
                ProjectKind(arguments.kind),
                arguments.audience,
                Visibility(arguments.visibility),
                arguments.parent,
                arguments.description,
            )
            return app.create_noninteractive(options, initialize_git=not arguments.no_git)
    except BuilderError as error:
        app.log.message("Fatal friendly error", error.render(), result=error.code)
        print(error.render(), file=sys.stderr)
        print(f"Full log: {app.log.path}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nCancelled. No additional action was taken.", file=sys.stderr)
        return 130
    return 1
