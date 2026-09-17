from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class FlyWireAnnotation:
    root_id: int
    cell_type: str = ""
    hemibrain_type: str = ""
    cell_class: str = ""
    cell_sub_class: str = ""
    super_class: str = ""
    flow: str = ""

    def searchable_text(self) -> str:
        return " ".join(
            (
                self.cell_type,
                self.hemibrain_type,
                self.cell_class,
                self.cell_sub_class,
                self.super_class,
                self.flow,
            )
        ).lower()


class FlyWireAnnotations:
    """Small dependency-free loader for FlyWire-style annotation tables.

    It intentionally focuses on stable, high-value columns and ignores extra
    columns rather than coupling FlyEcho to one particular dataset release.
    """

    ROOT_KEYS = ("root_id", "root", "rootid", "pt_root_id")

    def __init__(self, rows: Iterable[FlyWireAnnotation]) -> None:
        self.rows = list(rows)
        self.by_root_id = {row.root_id: row for row in self.rows}

    @staticmethod
    def _pick(fieldnames: list[str], candidates: tuple[str, ...], required: bool = False) -> str | None:
        lowered = {name.lower(): name for name in fieldnames}
        for key in candidates:
            if key in lowered:
                return lowered[key]
        if required:
            raise ValueError(f"Missing required column; expected one of {candidates}")
        return None

    @classmethod
    def from_path(cls, path: str | Path) -> "FlyWireAnnotations":
        path = Path(path)
        delimiter = "\t" if path.suffix.lower() in {".tsv", ".tab"} else ","
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            if not reader.fieldnames:
                raise ValueError("Annotation table has no header")

            fields = list(reader.fieldnames)
            root_key = cls._pick(fields, cls.ROOT_KEYS, required=True)
            optional = {
                "cell_type": cls._pick(fields, ("cell_type", "type")),
                "hemibrain_type": cls._pick(fields, ("hemibrain_type",)),
                "cell_class": cls._pick(fields, ("cell_class", "class")),
                "cell_sub_class": cls._pick(fields, ("cell_sub_class", "sub_class", "subclass")),
                "super_class": cls._pick(fields, ("super_class", "superclass")),
                "flow": cls._pick(fields, ("flow",)),
            }

            rows: list[FlyWireAnnotation] = []
            for raw in reader:
                value = (raw.get(root_key or "") or "").strip()
                if not value:
                    continue
                kwargs = {
                    name: ((raw.get(key) or "").strip() if key else "")
                    for name, key in optional.items()
                }
                rows.append(FlyWireAnnotation(root_id=int(value), **kwargs))
        return cls(rows)

    def get(self, root_id: int) -> FlyWireAnnotation | None:
        return self.by_root_id.get(int(root_id))

    def search(self, text: str, limit: int = 50) -> list[FlyWireAnnotation]:
        query = text.strip().lower()
        if not query:
            return self.rows[:limit]
        return [row for row in self.rows if query in row.searchable_text()][:limit]

    def root_ids_for_type(self, cell_type: str, exact: bool = True) -> list[int]:
        target = cell_type.strip().lower()
        if exact:
            return [row.root_id for row in self.rows if row.cell_type.lower() == target]
        return [row.root_id for row in self.rows if target in row.cell_type.lower()]

    def summary(self) -> dict[str, int]:
        return {
            "annotations": len(self.rows),
            "typed_neurons": sum(bool(row.cell_type) for row in self.rows),
            "unique_cell_types": len({row.cell_type for row in self.rows if row.cell_type}),
        }
