# pytest -q
from gkpo import canonicalize_and_hash
from adapters.dpo import dpo_to_gkpo, gkpo_to_dpo
from adapters.rrhf import rrhf_to_gkpo, gkpo_to_rrhf

def test_dpo_roundtrip():
    g = dpo_to_gkpo(delta_ref=0.1, beta=1.0)
    g2 = canonicalize_and_hash(g)
    cfg = gkpo_to_dpo(g2)
    assert abs(cfg["delta_ref"] - 0.1) < 1e-6

def test_rrhf_hash_diff():
    g_dpo = dpo_to_gkpo(delta_ref=0.0, beta=1.0)
    g_rrhf = rrhf_to_gkpo([{"name":"rank_margin_1","lambda":0.5}], delta_ref=0.0)
    assert g_dpo["provenance"]["opal_hash"] != g_rrhf["provenance"]["opal_hash"]

def test_flags_reference_shift():
    g = canonicalize_and_hash({"reference":{"form":"per_prompt"}, "weight":{"form":"constant","constant":1.0}})
    assert not g["reducibility"]["inside_R"]
    assert "reference_shift" in g["reducibility"]["reasons"]
