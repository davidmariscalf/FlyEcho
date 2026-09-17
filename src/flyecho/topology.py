from __future__ import annotations

from dataclasses import asdict, dataclass
import json


@dataclass(frozen=True)
class CircuitNode:
    name: str
    role: str
    biological_name: str
    scope: str


@dataclass(frozen=True)
class CircuitEdge:
    pre: str
    post: str
    kind: str
    evidence: str
    model_weight: float | None = None


ESCAPE_NODES: tuple[CircuitNode, ...] = (
    CircuitNode("LC4-like", "looming feature channel", "LC4", "visual input is replaced by echo-derived features"),
    CircuitNode("LPLC2-like", "looming feature channel", "LPLC2", "visual input is replaced by echo-derived features"),
    CircuitNode("GF-like", "descending escape command", "Giant Fiber", "central convergence motif"),
    CircuitNode("TTMn-like", "jump motor output", "TTMn", "downstream escape pathway"),
    CircuitNode("PSI-like", "flight relay", "PSI", "downstream escape pathway"),
    CircuitNode("DLMn-like", "flight motor output", "DLMn", "downstream escape pathway"),
)

ESCAPE_EDGES: tuple[CircuitEdge, ...] = (
    CircuitEdge("LC4-like", "GF-like", "excitatory", "direct looming-pathway convergence", 0.95),
    CircuitEdge("LPLC2-like", "GF-like", "excitatory", "direct looming-pathway convergence", 1.05),
    CircuitEdge("GF-like", "TTMn-like", "command", "giant-fiber jump branch", 3.0),
    CircuitEdge("GF-like", "PSI-like", "command", "giant-fiber flight branch", 3.0),
    CircuitEdge("PSI-like", "DLMn-like", "command", "flight motor relay", 3.0),
)


def node_names() -> tuple[str, ...]:
    return tuple(node.name for node in ESCAPE_NODES)


def edge_weight(pre: str, post: str) -> float:
    for edge in ESCAPE_EDGES:
        if edge.pre == pre and edge.post == post:
            if edge.model_weight is None:
                raise ValueError(f"Edge {pre!r} -> {post!r} has no model weight")
            return edge.model_weight
    raise KeyError(f"Unknown edge {pre!r} -> {post!r}")


def validate_topology() -> None:
    names = set(node_names())
    if len(names) != len(ESCAPE_NODES):
        raise ValueError("Circuit node names must be unique")
    seen: set[tuple[str, str]] = set()
    for edge in ESCAPE_EDGES:
        if edge.pre not in names or edge.post not in names:
            raise ValueError(f"Unknown node in edge {edge.pre!r} -> {edge.post!r}")
        key = (edge.pre, edge.post)
        if key in seen:
            raise ValueError(f"Duplicate edge {edge.pre!r} -> {edge.post!r}")
        seen.add(key)
        if edge.model_weight is not None and edge.model_weight < 0:
            raise ValueError("model_weight must be non-negative")


def topology_dict() -> dict[str, list[dict[str, object]]]:
    validate_topology()
    return {
        "nodes": [asdict(node) for node in ESCAPE_NODES],
        "edges": [asdict(edge) for edge in ESCAPE_EDGES],
    }


def topology_json(indent: int = 2) -> str:
    return json.dumps(topology_dict(), indent=indent, sort_keys=True)


def topology_dot() -> str:
    validate_topology()
    lines = ["digraph FlyEchoEscape {", "  rankdir=LR;"]
    for node in ESCAPE_NODES:
        label = f"{node.name}\\n{node.role}"
        lines.append(f'  "{node.name}" [label="{label}"];')
    for edge in ESCAPE_EDGES:
        label = edge.kind
        if edge.model_weight is not None:
            label += f" / model={edge.model_weight:g}"
        lines.append(f'  "{edge.pre}" -> "{edge.post}" [label="{label}"];')
    lines.append("}")
    return "\n".join(lines)
