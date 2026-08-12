"""Accessible, no-color text interface."""

from __future__ import annotations

from collections.abc import Callable, Sequence


class Console:
    def __init__(
        self,
        *,
        input_func: Callable[[str], str] = input,
        output_func: Callable[[str], None] = print,
    ) -> None:
        self._input = input_func
        self._output = output_func

    def write(self, message: str = "") -> None:
        self._output(message)

    def prompt(self, message: str, default: str = "") -> str:
        suffix = f" [{default}]" if default else ""
        answer = self._input(f"{message}{suffix}: ").strip()
        return answer or default

    def choose(self, question: str, options: Sequence[str]) -> int:
        if not options:
            raise ValueError("At least one option is required.")
        while True:
            self.write(question)
            for index, option in enumerate(options, 1):
                self.write(f"  {index}. {option}")
            answer = self.prompt("Enter a number")
            if answer.isdigit() and 1 <= int(answer) <= len(options):
                return int(answer) - 1
            self.write("Please enter one of the displayed numbers.")

    def confirm(self, question: str, *, default: bool = False) -> bool:
        hint = "Y/n" if default else "y/N"
        while True:
            answer = self._input(f"{question} [{hint}]: ").strip().lower()
            if not answer:
                return default
            if answer in {"y", "yes"}:
                return True
            if answer in {"n", "no"}:
                return False
            self.write("Please type yes or no.")

    def phrase(self, explanation: str, phrase: str) -> bool:
        self.write(explanation)
        return self._input(f"Type {phrase!r} to continue: ").strip() == phrase
