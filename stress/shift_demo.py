#!/usr/bin/env python3
# SHIFT: reference shift witness
import json
from gkpo import canonicalize_and_hash

g = {
  "version": "gkpo-1.0",
  "score": {"type": "logpi"},
  "weight": {"form": "constant","constant": 1.0},
  "reference": {"form": "per_prompt"},
  "link": "identity", "loss": "logistic", "beta": 1.0,
  "penalties": [],
  "provenance": {"method":"DPO-like (shift)","citations":["yang2023orpo"]},
  "reducibility": {"inside_R": False, "reasons": ["reference_shift"],
    "witness": {"raw_gap": 0.20, "delta_ref_prompt1": +0.50, "delta_ref_prompt2": -0.50}}
}
G = canonicalize_and_hash(g)
print(json.dumps(G["_canonical_serial"], indent=2))
print("opal_hash:", G["provenance"]["opal_hash"])
print("inside_R:", G["reducibility"]["inside_R"], "reasons:", G["reducibility"]["reasons"])
