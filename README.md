# Reproducibility budgets for ML preprints

A methods proposal introducing structured per-claim compute/time/dollar budgets and a corpus-level reproducibility-tax metric — a demonstration paper in the [rrxiv](https://rrxiv.com) reference corpus.

**Read the published paper:** [rrxiv.com/papers/rrxiv:2605.00003](https://rrxiv.com/papers/rrxiv:2605.00003)

## What this demonstrates

A methods proposal introducing structured per-claim compute/time/dollar budgets and a corpus-level 'reproducibility tax' metric. Six claims carrying quantified, checkable commitments a replicator can hold the paper to — an example of machine-verifiable promises encoded in the claim graph.

## Build it locally

This repo was created from the [rrxiv-paper-template](https://github.com/random-walks/rrxiv-paper-template).

```bash
./scripts/build.sh          # tectonic → build/main.pdf
./scripts/extract-cir.sh    # rrxiv parse → build/main.cir.json
./scripts/verify.sh         # validate the CIR against the rrxiv schema
```

The `rrxiv` CLI used by these scripts isn't on PyPI yet — install it from source:

```bash
pip install "rrxiv @ git+https://github.com/random-walks/rrxiv-python.git"
```

## License

Dual-licensed, matching the rest of the corpus:

- **Content** — the paper text and figures in `paper/`, plus `rrxiv-meta.json`, under [CC-BY-4.0](./LICENSE-CONTENT).
- **Code** — the `scripts/` and CI under [MIT](./LICENSE-CODE).
