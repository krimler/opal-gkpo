#!/usr/bin/env python3
# SCORE: score-dependent weight witness
import json
from gkpo import canonicalize_and_hash

g = {
  "version": "gkpo-1.0",
  "score": {"type": "logpi"},
  "weight": {"form": "score_dependent", "score_fn":"psi_piecewise"},
  "reference": {"form": "fixed_zero", "value": 0.0},
  "link": "identity", "loss": "logistic", "beta": 1.0,
  "penalties": [],
  "provenance": {"method":"SCORE"},
  "reducibility": {"inside_R": False, "reasons": ["score_dependent_weight"], "witness": {}}
}
G = canonicalize_and_hash(g)
print(json.dumps(G["_canonical_serial"], indent=2))
print("opal_hash:", G["provenance"]["opal_hash"])
print("inside_R:", G["reducibility"]["inside_R"], "reasons:", G["reducibility"]["reasons"])
