# FlyEcho

**Drosophila-connectome-inspired active sensing for obstacle detection.**

FlyEcho is a research/education repository that uses a small spiking neural network inspired by known *Drosophila* looming/escape circuitry to control an **ultrasonic emitter**, process echoes, and detect approaching objects.

> **Biological honesty:** a fruit-fly brain is not an ultrasonic radar and does not itself emit useful ranging waves. In FlyEcho, the "brain" is a computational model. A physical transducer emits the pulse; the neural model decides *when to ping* and interprets returned echoes.

## Why this is interesting

The system closes a real active-sensing loop:

```text
           echo-derived features
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   LC4-like              LPLC2-like
        └──────────┬──────────┘
                   ▼
                GF-like
              ┌────┴────┐
              ▼         ▼
          TTMn-like   PSI-like
           jump          │
                         ▼
                     DLMn-like
                       flight
                   │
         adaptive ping command
                   ▼
            ultrasonic sensor
                   │
                 object
                   │ echo
                   └──────────────► range tracker ──► brain
```

As an object approaches, the controller raises the ping rate. A GF-like output neuron produces a discrete `THREAT` event when the estimated time-to-collision becomes small enough, while the model also propagates the event into simplified jump and flight motor branches.

## What it can do

The default closed-loop demo provides:

- object presence and range
- approaching/receding classification
- closing speed
- approximate time-to-collision
- adaptive ultrasonic ping rate
- a spiking GF-like threat event
- simplified TTMn-like jump and PSI/DLMn-like flight-path activity
- deterministic circuit topology export as text, JSON or Graphviz DOT
- FlyWire-style connectivity CSV/TSV loading and local subgraph extraction
- FlyWire-style annotation-table loading and search
- an optional Brian2 implementation of the same six-node circuit motif
- optional ESP32 + HC-SR04 hardware operation

The default simulation is deterministic enough to test but contains configurable measurement noise.

## Quick start

Requires Python 3.10+.

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

pip install -e .
flyecho demo
```

Try a faster approaching object:

```bash
flyecho demo --distance 2.5 --velocity -0.65 --seconds 6
```

Inspect the explicit circuit definition:

```bash
flyecho circuit
flyecho circuit --format json
flyecho circuit --format dot > flyecho.dot
```

## Architecture

### 1. Echo front-end

`EchoSimulator` models a round-trip ultrasonic measurement:

\[
t_\mathrm{echo} = \frac{2d}{c}
\]

where `d` is target distance and `c` is the speed of sound.

### 2. Sensor encoding

Successive range measurements are converted into proximity drive, closing-speed drive, and time-to-collision drive. These values are turned into normalized model current.

### 3. Fly-inspired spiking circuit

The compact network deliberately resembles the *logic* of a Drosophila looming/escape pathway rather than claiming to be a faithful fly-brain simulation:

```text
closing / urgency ─► LC4-like ───┐
                                  ├─► GF-like ─► TTMn-like
proximity / urgency ─► LPLC2-like┘       │
                                         └─► PSI-like ─► DLMn-like
```

Every node in the lightweight backend is a leaky-integrate-and-fire neuron. The downstream TTMn/PSI/DLMn branch prevents the escape pathway from ending artificially at GF, but the normalized time constants, thresholds and synaptic weights are engineering parameters rather than fitted biological values.

`flyecho.topology` is the single source of truth for nodes, edges and normalized model weights. Both the lightweight controller and Brian2 backend consume the same topology so they cannot silently drift into different wiring diagrams.

### 4. Active ping controller

The network output controls sensing density: safe scenes use a lower ping rate, approaching obstacles raise it, and a GF-like spike temporarily drives maximum sampling. This makes the system **active**, not just a passive classifier.

## Biological grounding

Ache et al. showed that LC4 and LPLC2 are the primary direct visual inputs to the Drosophila Giant Fiber and that the GF combines their complementary looming information. The established downstream giant-fiber system then branches toward the jump and flight machinery: GF connects to TTMn and PSI, and PSI relays to DLM motor neurons.

FlyEcho does **not** claim that these neurons natively process ultrasound; echo features are deliberately mapped into analogous computational channels. It also does not claim that the simple LIF parameters reproduce measured Drosophila membrane dynamics or exact synaptic strengths.

Useful background:

- Ache et al. (2019), *Neural Basis for Looming Size and Velocity Encoding in the Drosophila Giant Fiber Escape Pathway*, Current Biology. DOI: `10.1016/j.cub.2019.01.079`.
- Klapoetke et al. (2017), *Ultra-selective looming detection from radial motion opponency*, Nature. DOI: `10.1038/nature24626`.
- Allen et al. (2006), *Making an escape: development and function of the Drosophila giant fibre system*, Seminars in Cell & Developmental Biology. DOI: `10.1016/j.semcdb.2005.11.011`.

## Brian2 backend

A mature simulator is preferable once the circuit grows beyond a toy network. FlyEcho therefore includes a Brian2 backend instead of extending the handwritten integrator indefinitely.

```bash
pip install -e ".[simulation]"
flyecho brian-demo
```

The package keeps Python 3.10+ support: Python 3.10/3.11 install the compatible Brian2 2.9 line, while Python 3.12+ uses Brian2 2.10.1+.

Brian2 here is a **cross-check and scale-up path**, not evidence that the normalized parameters are biologically fitted. GeNN is documented as a future high-scale option rather than added prematurely for a six-neuron circuit.

## Connectome workflow

The full adult-fly connectome contains far more neurons and synapses than this compact model. FlyEcho does not pretend that loading the connectome automatically produces sonar or a validated escape controller.

### Connectivity tables

```bash
flyecho connectome-summary my_edges.csv --min-weight 5 --hubs 20
```

`FlyWireEdgeList` supports strongest incoming/outgoing edges, weighted hubs, induced subgraphs and bounded multi-hop ego subgraphs.

### Annotation tables

```bash
flyecho annotations annotations.tsv --search LC4
```

`FlyWireAnnotations` recognizes the high-value FlyWire fields (`root_id`, `cell_type`, `hemibrain_type`, `cell_class`, `cell_sub_class`, `super_class`, `flow`) while ignoring unrelated columns so the loader is less brittle across table versions.

### Scientific connectome tools

```bash
pip install -e ".[connectome]"
```

This installs NAVis and neuprint-python. FlyWire annotations and fafbseg-py are documented as external data/access resources. See `data/README.md` and `docs/ECOSYSTEM.md`.

## Hardware mode

`firmware/esp32_ultrasonic/esp32_ultrasonic.ino` is a minimal ESP32 + HC-SR04 bridge. The firmware emits `RANGE,<metres>` and accepts `PING_HZ,<frequency>` commands, so the host model can control the physical sensor's sampling rate.

```bash
pip install -e ".[hardware]"
flyecho hardware --port COM3
# Linux example: flyecho hardware --port /dev/ttyUSB0
```

### Wiring

| HC-SR04 | ESP32 |
|---|---|
| VCC | 5V |
| GND | GND |
| TRIG | GPIO 5 |
| ECHO | GPIO 18 through a safe level divider |

Do **not** feed a 5 V HC-SR04 ECHO signal directly into a 3.3 V ESP32 input.

## Useful external repositories

FlyEcho now has a documented ecosystem rather than an unstructured list of dependencies:

- `brian-team/brian2` — integrated optional spiking simulator
- `navis-org/navis` — integrated optional morphology/connectivity toolkit
- `connectome-neuprint/neuprint-python` — integrated optional neuPrint client
- `flyconnectome/flywire_annotations` — annotation data source
- `navis-org/fafbseg-py` — future direct FlyWire/FAFB access
- `genn-team/genn` — future large-scale accelerated spiking simulation
- `NeLy-EPFL/flygym` — future embodied NeuroMechFly integration

See `docs/ECOSYSTEM.md` for the integration policy and rationale.

## Design principles

1. **No fake biology.** Biological inspiration and engineered substitutions are stated explicitly.
2. **Closed-loop sensing.** Neural state changes future sensor sampling.
3. **One topology, multiple backends.** Wiring and model weights are centralized.
4. **Reproducible tests.** Threat and motor-path propagation are covered by automated tests.
5. **Hardware optional.** Everything runs in simulation first.
6. **Connectome-ready.** Public data can be introduced without rewriting the core controller.
7. **Use mature tools when they add real capability.** Brian2/NAVis/neuPrint are optional integrations; GeNN/FlyGym remain documented future integrations until justified.

## Validation

GitHub Actions now exercises the dependency-free core on Python 3.10, 3.11 and 3.12, runs the Brian2 backend on Python 3.11 and 3.12, and smoke-tests the optional connectome stack. The test suite covers LIF behavior, tracking, threat/motor propagation, topology exports, FlyWire-style connectivity parsing, annotation parsing, hardware protocol helpers and the Brian2 integration.

## Scientific references

- Dorkenwald, S. et al. *Neuronal wiring diagram of an adult brain*. Nature 634, 124–138 (2024).
- Schlegel, P. et al. *Whole-brain annotation and multi-connectome cell typing of Drosophila*. Nature 634, 139–152 (2024).
- FlyWire: https://flywire.ai/
- FlyWire annotations: https://github.com/flyconnectome/flywire_annotations

## Safety and scope

FlyEcho is for benign sensing, robotics, education and neuroscience-inspired computing. It does not contain covert surveillance functionality or any mechanism for identifying people.

## License

MIT for the code in this repository. External simulators, tools and connectome datasets keep their own licenses and attribution requirements.
