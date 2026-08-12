"""Beginner workflows composed from small, testable services."""

from __future__ import annotations

import shutil
from pathlib import Path

from newbie_project_builder.commands import Runner
from newbie_project_builder.console import Console
from newbie_project_builder.errors import BuilderError
from newbie_project_builder.github import GitHub
from newbie_project_builder.host import detect
from newbie_project_builder.host import paths as build_paths
from newbie_project_builder.installer import Installer
from newbie_project_builder.integrations import Integrations
from newbie_project_builder.models import (
    Host,
    Paths,
    ProjectKind,
    ProjectOptions,
    Visibility,
    WorkflowState,
)
from newbie_project_builder.preflight import Preflight
from newbie_project_builder.project import Generator, slugify
from newbie_project_builder.state import StateStore
from newbie_project_builder.support import Support, members
from newbie_project_builder.technical_logging import OperationLog

PROJECT_LABELS = (
    ("Generic planning scaffold", ProjectKind.GENERIC),
    ("Python command-line tool", ProjectKind.PYTHON_CLI),
    ("Website", ProjectKind.WEB_APP),
    ("Web API", ProjectKind.WEB_API),
    ("Desktop application", ProjectKind.DESKTOP_APP),
    ("AI application", ProjectKind.AI_APP),
    ("Authorized security tool", ProjectKind.SECURITY_TOOL),
)
VISIBILITY_LABELS = (
    ("Private GitHub repository — recommended", Visibility.PRIVATE),
    ("Public GitHub repository", Visibility.PUBLIC),
    ("Local project only", Visibility.LOCAL_ONLY),
)


class Application:
    def __init__(
        self,
        *,
        home: Path | None = None,
        dry_run: bool = False,
        console: Console | None = None,
        host: Host | None = None,
    ) -> None:
        self.console = console or Console()
        self.host = host or detect()
        self.paths: Paths = build_paths(home)
        self.paths.ensure()
        self.log = OperationLog(self.paths)
        self.runner = Runner(self.log, dry_run=dry_run)
        self.preflight = Preflight(host=self.host)
        self.installer = Installer(self.host, self.runner)
        self.generator = Generator(self.paths, self.log, self.runner)
        self.github = GitHub(self.runner)
        self.integrations = Integrations(self.paths, self.runner)
        self.support = Support(self.paths, self.host)
        self.state = StateStore(self.paths.state)

    def banner(self) -> None:
        self.console.write("=" * 60)
        self.console.write(" NEWBIE PROJECT BUILDER")
        self.console.write(" Safe setup for people with no computer experience")
        self.console.write("=" * 60)
        self.console.write("No files are deleted and nothing is published without permission.")
        self.console.write(f"Technical log: {self.log.path}")
        self.console.write()

    def diagnostics(self) -> int:
        checks = self.preflight.run(self.paths.home)
        self.console.write("Computer check results:")
        for check in checks:
            self.console.write(f"[{check.marker}] {check.label}: {check.details}")
            if not check.passed and check.fix:
                self.console.write(f"       Fix: {check.fix}")
        required_failures = [check for check in checks if check.required and not check.passed]
        result = "PASS" if not required_failures else "NEEDS FIXES"
        self.log.message(
            "Diagnostics",
            "\n".join(f"[{check.marker}] {check.label}: {check.details}" for check in checks),
            result=result,
        )
        return 0 if not required_failures else 2

    def setup(self) -> int:
        state = WorkflowState(self.log.operation_id, "first-time-setup", next_step="diagnostics")
        self.state.save(state)
        self.diagnostics()
        self.state.complete(state, "diagnostics", "install-tools")
        tools = {tool.key: tool for tool in self.preflight.tools()}
        for key in ("git", "gh", "github_desktop"):
            tool = tools.get(key)
            if tool is None or tool.installed:
                continue
            try:
                plan = self.installer.plan(key)
            except BuilderError as error:
                self.console.write(error.render())
                continue
            self.console.write()
            self.console.write(f"Missing: {plan.name}")
            self.console.write(plan.explanation)
            for command in plan.commands:
                self.console.write(f"  Would run: {' '.join(command)}")
            if self.console.confirm(f"Install {plan.name} now?"):
                if not self.installer.execute(plan):
                    self.state.fail(state, "NPB-901", "install-tools")
                    return 1
                self.state.complete(state, f"install-{key}", "install-tools")
        self.state.complete(state, "install-tools", "integrations")
        self.show_integrations()
        self.state.complete(state, "integrations")
        self.console.write()
        self.console.write("Setup checks are complete. Restart the builder if any tool was installed.")
        return 0

    def show_integrations(self) -> int:
        self.console.write("AI integration status:")
        for status in self.integrations.statuses():
            marker = "PASS" if status.available else "FIX "
            self.console.write(f"[{marker}] {status.name}: {status.details}")
            self.console.write(f"       Next: {status.next_action}")
        return 0

    def install_agency(self) -> int:
        self.console.write("This downloads the official Agency Agents repository and installs")
        self.console.write("only the eight core roles into the current user's Codex agents folder.")
        self.console.write("It does not enable NEXUS or Agents Orchestrator.")
        if not self.console.confirm("Run the optional Agency Agents installation?"):
            self.console.write("No integration files were changed.")
            return 0
        return 0 if self.integrations.install_core_agents() else 1

    def _project_parent_default(self) -> Path:
        base = Path.home() / "Documents" if self.host.os_kind.value == "windows" else Path.home()
        return base / "GitHub-Projects"

    def project_wizard(self) -> int:
        name = self.console.prompt("What would you like to call the project?")
        project_slug = slugify(name)
        kind_index = self.console.choose(
            "What kind of project is this?",
            [label for label, _kind in PROJECT_LABELS],
        )
        audience = self.console.prompt("Who will use it?", "Only me")
        visibility_index = self.console.choose(
            "Where should the project live?",
            [label for label, _visibility in VISIBILITY_LABELS],
        )
        parent = Path(
            self.console.prompt("Parent folder", str(self._project_parent_default()))
        ).expanduser()
        description = self.console.prompt("One-sentence purpose", f"A new project named {name}.")
        options = ProjectOptions(
            name,
            project_slug,
            PROJECT_LABELS[kind_index][1],
            audience,
            VISIBILITY_LABELS[visibility_index][1],
            parent,
            description,
        )
        return self._create_with_confirmation(options)

    def _create_with_confirmation(self, options: ProjectOptions) -> int:
        files = self.generator.preview(options)
        self.console.write()
        self.console.write("Nothing has been created yet.")
        self.console.write(f"Project: {options.name}")
        self.console.write(f"Folder: {options.destination}")
        self.console.write(f"Type: {options.kind.value}")
        self.console.write(f"Visibility: {options.visibility.value}")
        self.console.write(f"Files to create: {len(files)}")
        if not self.console.phrase("Review the summary above.", "CREATE PROJECT"):
            self.console.write("Cancelled. No project files were created.")
            return 0
        state = WorkflowState(self.log.operation_id, "create-project", next_step="generate")
        self.state.save(state)
        result = self.generator.generate(options)
        self.state.complete(state, "generate", "local-commit")
        self.console.write(f"Project created at: {result.destination}")
        self.console.write(f"Files created: {len(result.created)}")
        if result.dry_run:
            self.console.write("Preview mode was active; no files were written.")
            return 0
        committed = False
        if result.git_initialized and self.console.confirm("Create the first local Git checkpoint?"):
            self._initial_commit(result.destination)
            committed = True
            self.state.complete(state, "local-commit", "github")
        if options.visibility is not Visibility.LOCAL_ONLY:
            if committed:
                self._offer_github(options, result.destination)
            else:
                self.console.write(
                    "GitHub publishing was skipped because the initial local checkpoint was not created."
                )
                self.log.message(
                    "GitHub publishing",
                    "Skipped because no initial commit was approved.",
                    result="SKIPPED",
                )
        self.state.complete(state, "github")
        self.console.write("Project workflow complete. Read README.md before adding code.")
        return 0

    def create_noninteractive(self, options: ProjectOptions, *, initialize_git: bool = True) -> int:
        result = self.generator.generate(options, initialize_git=initialize_git)
        self.console.write(f"Project {'previewed' if result.dry_run else 'created'}: {result.destination}")
        return 0

    def _initial_commit(self, project: Path) -> None:
        name = self.runner.run(
            ("git", "config", "--get", "user.name"),
            step="Check local Git author name",
            cwd=project,
            error_code="NPB-501",
            log_output=False,
        )
        email = self.runner.run(
            ("git", "config", "--get", "user.email"),
            step="Check local Git author email",
            cwd=project,
            error_code="NPB-501",
            log_output=False,
        )
        if not name.stdout.strip():
            author = self.console.prompt("Name to record in this project's commits")
            configured_name = self.runner.run(
                ("git", "config", "user.name", author),
                step="Set project-only Git author name",
                cwd=project,
                error_code="NPB-501",
                display_command=("git", "config", "user.name", "<USER-PROVIDED-NAME>"),
            )
            if not configured_name.ok:
                raise BuilderError("NPB-501", configured_name.stderr or configured_name.stdout)
        if not email.stdout.strip():
            address = self.console.prompt("Email to record in this project's commits")
            configured_email = self.runner.run(
                ("git", "config", "user.email", address),
                step="Set project-only Git author email",
                cwd=project,
                error_code="NPB-501",
                display_command=("git", "config", "user.email", "<USER-PROVIDED-EMAIL>"),
            )
            if not configured_email.ok:
                raise BuilderError("NPB-501", configured_email.stderr or configured_email.stdout)
        added = self.runner.run(
            ("git", "add", "."),
            step="Stage generated project files",
            cwd=project,
            error_code="NPB-501",
        )
        if not added.ok:
            raise BuilderError("NPB-501", added.stderr or added.stdout)
        committed = self.runner.run(
            ("git", "commit", "-m", "chore: initialize project"),
            step="Create initial local checkpoint",
            cwd=project,
            error_code="NPB-501",
        )
        if not committed.ok:
            raise BuilderError("NPB-501", committed.stderr or committed.stdout)

    def _offer_github(self, options: ProjectOptions, project: Path) -> None:
        if not shutil.which("gh"):
            self.console.write("GitHub CLI is missing. The project remains safe and local.")
            return
        if not self.github.signed_in():
            if not self.console.confirm("Sign in to GitHub using your browser?"):
                self.console.write("The project remains local.")
                return
            if not self.github.browser_login():
                raise BuilderError("NPB-201")
        account = self.github.account()
        self.console.write(f"Active GitHub account: {account.login}")
        self.console.write(f"Repository: {account.login}/{options.slug}")
        self.console.write(f"Visibility: {options.visibility.value.upper()}")
        if options.visibility is Visibility.PUBLIC and not self.console.phrase(
            "Public repositories can expose every committed file to the world.", "MAKE PUBLIC"
        ):
            self.console.write("Public repository creation cancelled; the project remains local.")
            return
        if not self.console.confirm("Create this GitHub repository?"):
            self.console.write("The project remains local.")
            return
        self.github.create_repository(
            project,
            name=options.slug,
            visibility=options.visibility,
            description=options.description,
        )
        if self.console.confirm("Publish the initial scaffold to GitHub now?"):
            self.github.publish_initial_main(project)

    def support_bundle(self) -> int:
        archive = self.support.create()
        self.console.write(f"Sanitized support bundle: {archive}")
        self.console.write("Contents:")
        for name in members(archive):
            self.console.write(f"  - {name}")
        self.console.write("Review the archive before sharing it.")
        return 0

    def latest_log(self) -> int:
        latest = OperationLog.latest(self.paths)
        self.console.write(f"Latest log: {latest or 'No log found.'}")
        return 0

    def cleanup(self) -> int:
        self.console.write("Cleanup removes only builder state, logs, support bundles, backups,")
        self.console.write(
            "and the builder-owned Agency checkout. Generated projects are excluded."
        )
        if not self.paths.marker.is_file():
            raise BuilderError(
                "NPB-901",
                f"Safety marker is missing; refusing cleanup under {self.paths.home}.",
            )
        if not self.console.phrase(
            "This action cannot be undone by the builder.", "DELETE BUILDER DATA"
        ):
            self.console.write("Cancelled. Nothing was deleted.")
            return 0
        for item in (
            self.paths.state,
            self.paths.logs,
            self.paths.support,
            self.paths.backups,
            self.paths.integrations,
        ):
            if not item.resolve().is_relative_to(self.paths.home.resolve()):
                raise BuilderError("NPB-901", f"Cleanup path escaped builder home: {item}")
            if item.is_dir():
                shutil.rmtree(item)
            elif item.exists():
                item.unlink()
        self.paths.ensure()
        self.console.write("Builder-owned data was removed. Generated projects were not touched.")
        return 0

    def menu(self) -> int:
        self.banner()
        while True:
            choice = self.console.choose(
                "What would you like to do?",
                (
                    "Set up this computer",
                    "Create a new project",
                    "Check or diagnose the computer",
                    "Show AI integration status",
                    "Install the Agency Agents core roster",
                    "Open the latest log location",
                    "Create a sanitized support bundle",
                    "Remove builder-owned data",
                    "Exit",
                ),
            )
            actions = (
                self.setup,
                self.project_wizard,
                self.diagnostics,
                self.show_integrations,
                self.install_agency,
                self.latest_log,
                self.support_bundle,
                self.cleanup,
            )
            if choice == len(actions):
                self.console.write("Goodbye. No additional changes were made.")
                return 0
            try:
                actions[choice]()
            except BuilderError as error:
                self.log.message("Friendly error", error.render(), result=error.code)
                self.console.write(error.render())
                self.console.write(f"Full log: {self.log.path}")
            self.console.write()
