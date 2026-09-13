from __future__ import annotations

from dataclasses import dataclass
import csv
from collections import defaultdict
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Edge:
    pre: int
    post: int
    weight: int


class FlyWireEdgeList:
    """Small, dependency-free loader for exported FlyWire-style edge lists."""

    PRE_KEYS = ("pre", "pre_id", "pre_root_id", "pre_pt_root_id")
    POST_KEYS = ("post", "post_id", "post_root_id", "post_pt_root_id")
    WEIGHT_KEYS = ("weight", "syn_count", "synapse_count", "neuropil_syn_count")

    def __init__(self, edges: Iterable[Edge]) -> None:
        self.edges = list(edges)
        self.outgoing: dict[int, list[Edge]] = defaultdict(list)
        self.incoming: dict[int, list[Edge]] = defaultdict(list)
        for edge in self.edges:
            self.outgoing[edge.pre].append(edge)
            self.incoming[edge.post].append(edge)

    @staticmethod
    def _pick(fieldnames: list[str], candidates: tuple[str, ...], label: str) -> str:
        lowered = {name.lower(): name for name in fieldnames}
        for key in candidates:
            if key in lowered:
                return lowered[key]
        raise ValueError(f"Could not find {label} column. Available: {fieldnames}")

    @classmethod
    def from_csv(cls, path: str | Path, min_weight: int = 1) -> "FlyWireEdgeList":
        with open(path, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError("CSV has no header")
            pre_k = cls._pick(reader.fieldnames, cls.PRE_KEYS, "presynaptic")
            post_k = cls._pick(reader.fieldnames, cls.POST_KEYS, "postsynaptic")
            w_k = cls._pick(reader.fieldnames, cls.WEIGHT_KEYS, "weight")
            edges = []
            for row in reader:
                w = int(float(row[w_k]))
                if w >= min_weight:
                    edges.append(Edge(int(row[pre_k]), int(row[post_k]), w))
        return cls(edges)

    def strongest_outgoing(self, neuron_id: int, limit: int = 20) -> list[Edge]:
        return sorted(self.outgoing.get(neuron_id, []), key=lambda e: e.weight, reverse=True)[:limit]

    def summary(self) -> dict[str, int]:
        nodes = set()
        for e in self.edges:
            nodes.add(e.pre)
            nodes.add(e.post)
        return {
            "neurons": len(nodes),
            "edges": len(self.edges),
            "total_synaptic_weight": sum(e.weight for e in self.edges),
        }
