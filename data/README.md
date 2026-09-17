# Connectome data

This repository intentionally does **not** redistribute the FlyWire connectome.

Recommended sources:

- FlyWire / Codex: https://codex.flywire.ai/
- FlyWire project: https://flywire.ai/
- FlyWire annotation repository: https://github.com/flyconnectome/flywire_annotations
- Connectivity dataset referenced by the 2024 whole-brain papers: https://doi.org/10.5281/zenodo.10676866
- NAVis: https://github.com/navis-org/navis
- fafbseg-py: https://github.com/navis-org/fafbseg-py

See `docs/ECOSYSTEM.md` for why each external repository is useful and which ones are actually integrated.

## Why the data is not bundled

The connectome is large, versioned and externally licensed. Keeping it out of the repo makes provenance explicit and prevents an old snapshot from silently becoming the "truth".

## Using an exported edge list

CSV and TSV are both accepted. Common FlyWire-style column names such as `pre_root_id`, `post_root_id` and `syn_count` are detected automatically.

```python
from flyecho.connectome import FlyWireEdgeList

g = FlyWireEdgeList.from_csv("my_edges.csv", min_weight=5)
print(g.summary())
print(g.strongest_outgoing(720575940000000000))
print(g.strongest_incoming(720575940000000000))
print(g.hubs(limit=20))
```

A local neighborhood can be extracted without loading a graph library:

```python
local = g.ego_subgraph(
    [720575940000000000],
    hops=2,
    min_weight=5,
    max_nodes=200,
)
print(local.summary())
```

CLI equivalent:

```bash
flyecho connectome-summary my_edges.csv --min-weight 5 --hubs 20
```

## Using FlyWire annotations

The public FlyWire annotation tables contain fields such as `root_id`, `cell_type`, `cell_class`, `super_class`, `flow` and `hemibrain_type`. FlyEcho can load a local CSV/TSV export without pulling in pandas:

```python
from flyecho.annotations import FlyWireAnnotations

a = FlyWireAnnotations.from_path("annotations.tsv")
print(a.summary())
print(a.root_ids_for_type("LC4"))
print(a.search("descending"))
```

CLI equivalent:

```bash
flyecho annotations annotations.tsv --search LC4
```

## Optional connectome stack

For morphology, visualization and direct remote-dataset work:

```bash
pip install -e ".[connectome]"
```

This installs NAVis and neuprint-python. Direct FlyWire access through fafbseg-py remains an advanced/reference integration rather than a mandatory dependency.

## Research direction

The next defensible step is not to simulate the whole fly brain and call it sonar. It is to identify a sensory-to-descending pathway using real annotations/connectivity, extract a constrained subgraph, compare its dynamics with the compact engineered network, and only then decide which additional neurons are justified.
