#!/usr/bin/env python3
from typing import Dict, Any, List
from gkpo import canonicalize_and_hash

def rrhf_to_gkpo(penalties: List[Dict[str, float]], delta_ref: float = 0.0, beta: float = 1.0, citations=None) -> Dict[str, Any]:
    citations = citations or ["yuan2023rrhf"]
    g = {
        "version": "gkpo-1.0",
        "score": {"type": "logpi"},
        "weight": {"form": "constant", "constant": 1.0},
        "reference": {"form": "fixed_scalar", "value": float(delta_ref)},
        "link": "identity", "loss": "logistic", "beta": float(beta),
        "penalties": [{"name": p["name"], "lambda": float(p["lambda"])} for p in penalties],
        "dataset_ops": {"group_weights": [], "group_penalties": [], "composition": "dataset_then_policy"},
        "provenance": {"method": "RRHF", "citations": citations},
        "reducibility": {"inside_R": True, "reasons": [], "witness": {}}
    }
    return canonicalize_and_hash(g)

def gkpo_to_rrhf(g: Dict[str, Any]) -> Dict[str, Any]:
    g2 = canonicalize_and_hash(g)
    if not g2["reducibility"]["inside_R"]:
        raise ValueError(f"Not reducible to RRHF: {g2['reducibility']['reasons']}")
    pens = [{"name": p["name"], "lambda": p["lambda"]} for p in g2.get("penalties", [])]
    return {"penalties": pens, "delta_ref": g2.get("reference", {}).get("value", 0.0), "beta": g2.get("beta", 1.0)}
