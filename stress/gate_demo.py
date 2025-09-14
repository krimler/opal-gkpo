#!/usr/bin/env python3
# GATE: non-additive gate witness
import json
from gkpo import canonicalize_and_hash

g = {
  "version": "gkpo-1.0",
  "score": {"type": "logpi"},
  "weight": {"form": "constant","constant": 1.0},
  "reference": {"form": "fixed_zero", "value": 0.0},
  "link": "identity", "loss": "logistic", "beta": 1.0,
  "penalties": [
    {"name":"phi1","lambda":1.0,"meta":{"gate":False}},
    {"name":"phi2_gate_on_phi1_zero","lambda":1.0,"meta":{"gate":True}}
  ],
  "provenance": {"method":"GATED"},
  "reducibility": {"inside_R": False, "reasons": ["non_additive_gate"],
    "witness": {"phi_pairs":[[1,10],[0,1]],"phi_value_equal":1.0}}
}
G = canonicalize_and_hash(g)
print(json.dumps(G["_canonical_serial"], indent=2))
print("opal_hash:", G["provenance"]["opal_hash"])
print("inside_R:", G["reducibility"]["inside_R"], "reasons:", G["reducibility"]["reasons"])
