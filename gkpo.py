#!/usr/bin/env python3
# GKPO reference: schema, canonicalization, deterministic opal_hash, reducibility flags.
import argparse, json, sys, hashlib
from typing import Any, Dict, List

ROUND_PLACES = 6
SCHEMA_VERSION = "gkpo-1.0"

def _round_num(x: Any):
    if isinstance(x, int):
        return x
    if isinstance(x, float):
        return float(f"{x:.{ROUND_PLACES}f}")
    return x

def _round_all_numbers(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _round_all_numbers(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round_all_numbers(v) for v in obj]
    return _round_num(obj)

def _sorted_obj(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _sorted_obj(obj[k]) for k in sorted(obj.keys())}
    if isinstance(obj, list):
        return [_sorted_obj(v) for v in obj]
    return obj

def _json_compact(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=False).encode("utf-8")

def _canonicalize_weight(w: Dict[str, Any]) -> Dict[str, Any]:
    w = dict(w or {})
    w.setdefault("form", "constant")
    if w["form"] == "constant":
        w["constant"] = _round_num(float(w.get("constant", 1.0)))
    elif w["form"] == "score_dependent":
        # keep as-is but canonical
        pass
    if "factors" in w and isinstance(w["factors"], list):
        w["factors"] = sorted([str(s) for s in w["factors"]])
    return w

def _canonical_sort_penalties(pens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for p in pens or []:
        q = dict(p)
        if "lambda" in q:
            q["lambda"] = _round_num(q["lambda"])
        if "meta" in q and isinstance(q["meta"], dict):
            q["meta"] = {k: q["meta"][k] for k in sorted(q["meta"].keys())}
        out.append(q)
    out.sort(key=lambda z: str(z.get("name", "")))
    return out

def _infer_reducibility(gkpo: Dict[str, Any]) -> Dict[str, Any]:
    reasons = []
    ref_form = ((gkpo.get("reference") or {}).get("form") or "fixed_zero")
    if ref_form not in {"fixed_zero", "fixed_scalar"}:
        reasons.append("reference_shift")
    wform = ((gkpo.get("weight") or {}).get("form") or "constant")
    if wform == "score_dependent":
        reasons.append("score_dependent_weight")
    for p in gkpo.get("penalties") or []:
        if (p.get("meta") or {}).get("gate", False):
            reasons.append("non_additive_gate")
            break
    return {"inside_R": len(reasons) == 0, "reasons": reasons, "witness": gkpo.get("reducibility", {}).get("witness", {})}

def canonicalize_and_hash(gkpo: Dict[str, Any]) -> Dict[str, Any]:
    g = dict(gkpo)
    g.setdefault("version", SCHEMA_VERSION)
    g["weight"] = _canonicalize_weight(g.get("weight") or {"form": "constant", "constant": 1.0})
    g.setdefault("reference", {"form": "fixed_zero", "value": 0.0})
    g.setdefault("link", "identity")
    g.setdefault("loss", "logistic")
    g.setdefault("beta", 1.0)
    g["penalties"] = _canonical_sort_penalties(g.get("penalties") or [])
    g.setdefault("dataset_ops", {"group_weights": [], "group_penalties": [], "composition": "dataset_then_policy"})
    g.setdefault("provenance", {})
    red = _infer_reducibility(g)
    g["reducibility"] = {"inside_R": red["inside_R"], "reasons": red["reasons"], "witness": red["witness"]}

    serial = {
        "version": g["version"],
        "score": g.get("score"),
        "weight": g["weight"],
        "reference": g["reference"],
        "link": g["link"],
        "loss": g["loss"],
        "beta": g["beta"],
        "penalties": g["penalties"],
        "dataset_ops": g["dataset_ops"],
        "reducibility": g["reducibility"],
        "provenance": {k: g["provenance"].get(k) for k in ["method", "citations", "notes"]},
    }
    serial = _round_all_numbers(serial)
    serial = _sorted_obj(serial)
    blob = _json_compact(serial)
    h = hashlib.sha256(blob).hexdigest()
    g["provenance"]["opal_hash"] = h
    g["_canonical_serial"] = json.loads(blob.decode("utf-8"))
    return g

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-json", help="Load GKPO JSON and print canonical JSON + opal_hash")
    ap.add_argument("--check", nargs="+", help="Check one or more GKPO JSON files (hash + flags)")
    args = ap.parse_args()

    if args.from_json:
        with open(args.from_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        g = canonicalize_and_hash(data)
        print(json.dumps(g["_canonical_serial"], indent=2, ensure_ascii=False))
        print("opal_hash:", g["provenance"]["opal_hash"])
        print("inside_R:", g["reducibility"]["inside_R"], "reasons:", g["reducibility"]["reasons"])
        if g["reducibility"]["witness"]:
            print("witness:", json.dumps(g["reducibility"]["witness"], indent=2))
        return

    if args.check:
        for path in args.check:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            g = canonicalize_and_hash(data)
            print(f"{path}: {g['provenance']['opal_hash']} | inside_R={g['reducibility']['inside_R']} reasons={g['reducibility']['reasons']}")
        return

    ap.print_help()

if __name__ == "__main__":
    main()
