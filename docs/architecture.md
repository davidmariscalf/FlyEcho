# Architecture notes

## What "using the fly brain" means here

There are three increasingly literal levels.

### Level A — implemented

A compact spiking neural network uses motifs and cell names inspired by Drosophila looming/escape processing. LC4-like and LPLC2-like channels converge in parallel onto a GF-like output. This is fast, testable, and useful for active sensing.

### Level B — supported by the data adapter

Extract a subgraph from FlyWire and use measured connectivity to replace some hand-written weights. This is scientifically more interesting and still computationally manageable.

### Level C — whole-connectome simulation

Possible, but misleading if the sensory interface is arbitrary. The whole connectome evolved for a fly's native sensory organs, not an ultrasonic transducer. A full simulation without a defensible encoding layer adds scale without necessarily adding validity.

## Active sensing loop

1. Emit pulse.
2. Estimate range from return delay.
3. Track range rate.
4. Encode proximity, approach and TTC.
5. Run the spiking circuit.
6. Adapt the next ping interval.
7. Raise a discrete threat event when the descending output spikes.

The key property is step 6: perception affects how the system samples the world next.

## Future experiments

- Replace range-rate features with raw echo-envelope spike encoding.
- Extract a FlyWire subgraph around visual looming and descending neurons.
- Compare engineered and data-derived networks on the same collision dataset.
- Add a second transducer for left/right steering.
- Add optical-flow input and test multisensory fusion.
- Port the LIF core to a microcontroller or neuromorphic board.
