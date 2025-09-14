# Opal & GKPO (artifact)

This artifact accompanies the paper **“Opal: An Operator Algebra View for RLHF (with the GKPO Interchange Schema)”**.

## Contents
- `gkpo.py`: GKPO schema, canonicalization, deterministic `opal_hash`, reducibility flags.
- `adapters/`: tiny adapters for DPO and RRHF.
- `stress/`: SHIFT / GATE / SCORE finite-witness demos (toy numbers).
- `examples/`:
  - `dpo_min.json`: minimal DPO-like GKPO.
  - `rrhf_min.json`: RRHF via additive penalties.
  - `pporm_min.json`: PPO-RM with KL anchor (fixed reference).
  - `orpo_shift.json`: example outside R (prompt-varying reference).
- `tests/test_roundtrip.py`: minimal checks.
- `equivalence_demo.py`: basic equivalence demo
## Quickstart
```bash
python gkpo.py --from-json examples/dpo_min.json
python gkpo.py --from-json examples/rrhf_min.json
python gkpo.py --from-json examples/pporm_min.json
python gkpo.py --check examples/*.json
PYTHONPATH=. python stress/shift_demo.py
PYTHONPATH=. python stress/gate_demo.py
PYTHONPATH=. python stress/score_demo.py
python equivalence_demo.py examples/dpo_min.json examples/rrhf_min.json
python equivalence_demo.py examples/dpo_min.json examples/pporm_min.json --show-diff
```
