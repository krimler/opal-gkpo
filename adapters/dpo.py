#!/usr/bin/env python3
from typing import Dict, Any
from gkpo import canonicalize_and_hash

def dpo_to_gkpo(delta_ref: float = 0.0, beta: float = 1.0, citations=None) -> Dict[str, Any]:
    citations = citations or ["rafailov2023direct"]
    g = {
        "version": "gkpo-1.0",
        "score": {"type": "logpi"},
        "weight": {"form": "constant", "constant": 1.0},
        "reference": {"form": "fixed_scalar", "value": float(delta_ref)},
        "link": "identity", "loss": "logistic", "beta": float(beta),
        "penalties": [],
        "dataset_ops": {"group_weights": [], "group_penalties": [], "composition": "dataset_then_policy"},
        "provenance": {"method": "DPO", "citations": citations},
        "reducibility": {"inside_R": True, "reasons": [], "witness": {}}
    }
    return canonicalize_and_hash(g)

def gkpo_to_dpo(g: Dict[str, Any]) -> Dict[str, Any]:
    g2 = canonicalize_and_hash(g)
    if not g2["reducibility"]["inside_R"]:
        raise ValueError(f"Not reducible to DPO: {g2['reducibility']['reasons']}")
    ref = g2.get("reference", {})
    return {"delta_ref": float(ref.get("value", 0.0)), "beta": float(g2.get("beta", 1.0)),
            "loss": g2.get("loss", "logistic"), "link": g2.get("link", "identity")}
