"""What a chord-spacing migration reports to the reviewer (C3a, D-123)."""
from collections import Counter
from dataclasses import dataclass, field


@dataclass
class Report:
    """What the tool did, for the reviewer."""
    lines: list[str] = field(default_factory=list)
    stats: Counter = field(default_factory=Counter)

    def note(self, stat: str, song: str, line: int, message: str, context: str = "") -> None:
        self.stats[stat] += 1
        suffix = f"  {context}" if context else ""
        self.lines.append(f"{song}:{line}: {message}{suffix}")


def clean(text: str) -> str:
    return text.replace("\n", "⏎")


def line_of(src: str, offset: int) -> int:
    return src.count("\n", 0, offset) + 1
