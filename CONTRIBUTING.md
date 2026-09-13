# Contributing to FlyEcho

Thanks for testing FlyEcho. The most useful contributions are reproducible measurements, bug reports, and biologically grounded improvements.

Please include your operating system and Python version, the exact command you ran, expected versus observed behaviour, and the full traceback when relevant. For hardware tests, also include the transducer, microcontroller, approximate target material, distance range and room conditions.

## Development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
```

## Scientific claims

Please distinguish between established Drosophila biology, connectome-derived structure, and engineering abstractions introduced by FlyEcho. New biological claims should cite primary literature or the relevant connectome data release.
