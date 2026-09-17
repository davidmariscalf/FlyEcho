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
    """Dependency-free loader and explorer for FlyWire-style edge lists."""

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
    def from_csv(
        cls,
        path: str | Path,
        min_weight: int = 1,
        delimiter: str | None = None,
    ) -> "FlyWireEdgeList":
        path = Path(path)
        if min_weight < 1:
            raise ValueError("min_weight must be >= 1")
        if delimiter is None:
            delimiter = "\t" if path.suffix.lower() in {".tsv", ".tab"} else ","

        with path.open("r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
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
        return sorted(self.outgoing.get(int(neuron_id), []), key=lambda e: e.weight, reverse=True)[:limit]

    def strongest_incoming(self, neuron_id: int, limit: int = 20) -> list[Edge]:
        return sorted(self.incoming.get(int(neuron_id), []), key=lambda e: e.weight, reverse=True)[:limit]

    def neighbors(self, neuron_id: int) -> set[int]:
        neuron_id = int(neuron_id)
        return {
            *(edge.post for edge in self.outgoing.get(neuron_id, [])),
            *(edge.pre for edge in self.incoming.get(neuron_id, [])),
        }

    def induced_subgraph(self, neuron_ids: Iterable[int], min_weight: int = 1) -> "FlyWireEdgeList":
        nodes = {int(node) for node in neuron_ids}
        return FlyWireEdgeList(
            edge
            for edge in self.edges
            if edge.weight >= min_weight and edge.pre in nodes and edge.post in nodes
        )

    def ego_subgraph(
        self,
        seed_ids: Iterable[int],
        *,
        hops: int = 1,
        min_weight: int = 1,
        max_nodes: int = 500,
    ) -> "FlyWireEdgeList":
        """Expand a local connectivity neighborhood around one or more seeds."""

        if hops < 0:
            raise ValueError("hops must be >= 0")
        if max_nodes < 1:
            raise ValueError("max_nodes must be >= 1")

        selected = {int(node) for node in seed_ids}
        frontier = set(selected)

        for _ in range(hops):
            next_frontier: set[int] = set()
            for node in frontier:
                for edge in self.outgoing.get(node, []):
                    if edge.weight >= min_weight:
                        next_frontier.add(edge.post)
                for edge in self.incoming.get(node, []):
                    if edge.weight >= min_weight:
                        next_frontier.add(edge.pre)

            next_frontier -= selected
            room = max_nodes - len(selected)
            if room <= 0:
                break
            if len(next_frontier) > room:
                ranked = sorted(
                    next_frontier,
                    key=self.total_incident_weight,
                    reverse=True,
                )
                next_frontier = set(ranked[:room])
            selected.update(next_frontier)
            frontier = next_frontier
            if not frontier:
                break

        return self.induced_subgraph(selected, min_weight=min_weight)

    def total_incident_weight(self, neuron_id: int) -> int:
        neuron_id = int(neuron_id)
        return sum(e.weight for e in self.outgoing.get(neuron_id, [])) + sum(
            e.weight for e in self.incoming.get(neuron_id, [])
        )

    def hubs(self, limit: int = 20) -> list[tuple[int, int]]:
        nodes = set(self.outgoing) | set(self.incoming)
        ranked = ((node, self.total_incident_weight(node)) for node in nodes)
        return sorted(ranked, key=lambda item: item[1], reverse=True)[:limit]

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
