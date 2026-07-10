from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal


@dataclass(frozen=True)
class ValidationIssue:
    severity: Literal["error", "warning"]
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationResult:
    pet_id: str
    pet_dir: Path
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    def add(
        self,
        severity: Literal["error", "warning"],
        code: str,
        message: str,
        path: Path | str | None = None,
    ) -> None:
        self.issues.append(
            ValidationIssue(
                severity=severity,
                code=code,
                message=message,
                path=str(path) if path is not None else None,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "petId": self.pet_id,
            "petDir": str(self.pet_dir),
            "ok": self.ok,
            "issues": [issue.to_dict() for issue in self.issues],
        }
