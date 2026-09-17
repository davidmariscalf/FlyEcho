# FlyEcho scientific ecosystem

FlyEcho keeps its core dependency-free and treats larger neuroscience projects as optional tools or data sources. This prevents a small educational controller from silently turning into an unmaintainable stack while still giving the project a credible path toward larger circuits.

## Integrated optional tools

### brian-team/brian2

Repository: https://github.com/brian-team/brian2

Purpose: established spiking-neural-network simulator. FlyEcho now includes an optional Brian2 backend for the six-node escape motif. Install with:

```bash
pip install -e ".[simulation]"
flyecho brian-demo
```

Python compatibility is handled in `pyproject.toml`: Python 3.10/3.11 use the compatible Brian2 2.9 line, while Python 3.12+ can use Brian2 2.10.1+.

### navis-org/navis

Repository: https://github.com/navis-org/navis

Purpose: neuron morphology, connectivity analysis, plotting and interfaces to remote connectome services. It is part of the optional `connectome` extra rather than a core dependency.

### connectome-neuprint/neuprint-python

Repository: https://github.com/connectome-neuprint/neuprint-python

Purpose: programmatic access to neuPrint datasets. It is installed with the optional `connectome` extra so future FlyEcho analyses can query published connectomes without reimplementing a client.

## Data and FlyWire tooling

### flyconnectome/flywire_annotations

Repository: https://github.com/flyconnectome/flywire_annotations

Purpose: authoritative public annotation tables for the adult-fly connectome. FlyEcho's `FlyWireAnnotations` loader accepts the high-value annotation columns while ignoring unrelated extra columns, reducing coupling to one table version.

### navis-org/fafbseg-py

Repository: https://github.com/navis-org/fafbseg-py

Purpose: FlyWire/FAFB data access and analysis. This is not installed by default because it brings a larger data-access stack and may require credentials or dataset-specific setup. It is the natural next adapter when FlyEcho moves from local exports to direct FlyWire queries.

## Scale-up and embodiment references

### genn-team/genn

Repository: https://github.com/genn-team/genn

Purpose: high-performance simulation for much larger spiking networks. It is deliberately not a dependency today. For six neurons Brian2 is the more proportionate choice; GeNN becomes interesting only if FlyEcho grows to thousands or more simulated neurons.

### NeLy-EPFL/flygym

Repository: https://github.com/NeLy-EPFL/flygym

Purpose: NeuroMechFly/FlyGym provides an embodied adult-fly simulation with sensory and motor interfaces. FlyGym 2.x is a future route for testing whether a FlyEcho-derived descending command can drive an embodied model rather than only a scalar `THREAT` output. It currently requires Python 3.12+, so it remains a reference integration instead of a FlyEcho dependency.

## Integration policy

A repository is added to the core package only when FlyEcho directly calls it and automated tests can exercise the integration. Repositories that are useful but heavy, dataset-specific or premature are documented here instead of being vendored or added as unconditional dependencies.

This distinction matters scientifically: connecting more repositories does not make the model more biologically faithful. New dependencies should correspond to a measurable capability such as validated spiking dynamics, real connectome access, morphology analysis or embodied behavior.
