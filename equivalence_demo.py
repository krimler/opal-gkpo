#!/usr/bin/env python3
"""
equivalence_demo.py — Compare two GKPO JSON configs for equivalence.

Usage:
  python equivalence_demo.py A.json B.json
  python equivalence_demo.py A.json B.json --show-diff
  python equivalence_demo.py --help

Equivalence criterion:
  - Canonicalization via gkpo.canonicalize_and_hash
  - Equality if and only if opal_hash is identical (hash of canonical JSON).
  - Also reports reducibility flags and field-level differences when requested.
"""
import argparse, json, sys
from typing import Any, Dict, List, Tuple

try:
    from gkpo import canonicalize_and_hash
except Exception as e:
    print("Error: could not import gkpo.py from current directory. Make sure this script sits next to gkpo.py.", file=sys.stderr)
    raise

def _load(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _flatten(d: Any, prefix: str = "") -> Dict[str, Any]:
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(_flatten(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(d, list):
        out[prefix] = d  # keep list as unit
    else:
        out[prefix] = d
    return out

def _dict_diff(a: Dict[str, Any], b: Dict[str, Any], ignore_keys: List[str]) -> List[Tuple[str, Any, Any]]:
    fa, fb = _flatten(a), _flatten(b)
    keys = set(fa.keys()) | set(fb.keys())
    diffs = []
    for k in sorted(keys):
        if any(k.startswith(ig) for ig in ignore_keys):
            continue
        va, vb = fa.get(k, "<MISSING>"), fb.get(k, "<MISSING>")
        if va != vb:
            diffs.append((k, va, vb))
    return diffs

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Compare two GKPO JSON files for equivalence via canonicalization.")
    p.add_argument("json_a", help="First GKPO JSON")
    p.add_argument("json_b", help="Second GKPO JSON")
    p.add_argument("--show-diff", action="store_true", help="Print field-level differences (canonical serial)")
    p.add_argument("--ignore", nargs="*", default=["provenance"], help="Top-level canonical keys to ignore when diffing")
    args = p.parse_args(argv)

    A = _load(args.json_a)
    B = _load(args.json_b)

    GA = canonicalize_and_hash(A)
    GB = canonicalize_and_hash(B)

    hash_a = GA.get("provenance", {}).get("opal_hash")
    hash_b = GB.get("provenance", {}).get("opal_hash")
    inside_a = GA.get("reducibility", {}).get("inside_R")
    inside_b = GB.get("reducibility", {}).get("inside_R")
    reasons_a = GA.get("reducibility", {}).get("reasons", [])
    reasons_b = GB.get("reducibility", {}).get("reasons", [])

    print("== GKPO Equivalence Report ==")
    print(f"A: {args.json_a}")
    print(f"B: {args.json_b}")
    print(f"opal_hash A: {hash_a}")
    print(f"opal_hash B: {hash_b}")
    print(f"inside_R  A: {inside_a}  reasons: {reasons_a}")
    print(f"inside_R  B: {inside_b}  reasons: {reasons_b}")
    equal = (hash_a == hash_b)
    print("\nEquivalent (by hash)?", "YES" if equal else "NO")

    if args.show_diff or not equal:
        print("\n-- Canonical diff (excluding ignored keys) --")
        diffs = _dict_diff(GA.get("_canonical_serial", {}), GB.get("_canonical_serial", {}), ignore_keys=args.ignore)
        if not diffs:
            print("(no differences)")
        else:
            for k, va, vb in diffs:
                # compact print
                sa = json.dumps(va, ensure_ascii=False)
                sb = json.dumps(vb, ensure_ascii=False)
                if len(sa) > 120: sa = sa[:117] + "..."
                if len(sb) > 120: sb = sb[:117] + "..."
                print(f"{k}:\n  A={sa}\n  B={sb}\n")

    # Return nonzero exit if not equal (useful in CI)
    return 0 if equal else 1

if __name__ == "__main__":
    sys.exit(main())
