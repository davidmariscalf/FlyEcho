# Connectome data

This repository intentionally does **not** redistribute the FlyWire connectome.

Recommended sources:

- FlyWire / Codex: https://codex.flywire.ai/
- FlyWire project: https://flywire.ai/
- FlyWire annotation repository: https://github.com/flyconnectome/flywire_annotations
- Connectivity dataset referenced by the 2024 whole-brain papers: https://doi.org/10.5281/zenodo.10676866

## Why the data is not bundled

The connectome is large, versioned and externally licensed. Keeping it out of the repo makes provenance explicit and prevents an old snapshot from silently becoming the "truth".

## Using an exported CSV

```python
from flyecho.connectome import FlyWireEdgeList

g = FlyWireEdgeList.from_csv("my_edges.csv", min_weight=5)
print(g.summary())
print(g.strongest_outgoing(720575940000000000))
```

The next sensible research step is not to simulate all neurons and call it radar. It is to identify a defensible sensory-to-descending pathway, extract that subgraph, then compare its dynamics with the compact engineered network.
