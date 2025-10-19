#!/usr/bin/env python3
import argparse
from collections import defaultdict
from typing import List, Tuple

from inference import (
    load_data,
    select_next_symptoms,
    update_posteriors_positive,
    calculate_confidence,
    categorize_symptom,
    compute_scarcity_boosts,
    dynamic_required_hits,
    CLUSTERS,
    EARLY_FINALIZE_TOPP,
    SUCCESS_CONFIDENCE,
    MIN_EVIDENCE_ANSWERS,
)


def count_evidence_symptoms_for_disease(symptom_map: dict, disease_id: int) -> int:
    count = 0
    for sym, did_map in symptom_map.items():
        if disease_id in did_map and did_map[disease_id].get("lr_pos") is not None:
            count += 1
    return count


def list_disease_symptoms():
    diseases, _priors, symptom_map = load_data()
    print("Disease | Evidence-backed symptoms (pos LR)")
    for did, info in diseases.items():
        syms = [s for s, dm in symptom_map.items() if did in dm and dm[did].get("lr_pos") is not None]
        syms.sort()
        print(f"{info['name']} | {', '.join(syms) if syms else '(none)'}")


def pick_target_symptom(next_syms: List[str], target_id: int, symptom_map: dict) -> str:
    for sym in next_syms:
        lr_pos = symptom_map.get(sym, {}).get(target_id, {}).get("lr_pos")
        if lr_pos is not None and lr_pos > 1.0:
            return sym
    return ""


def simulate_target(target_id: int, max_steps: int = 6) -> Tuple[bool, int, str, float, int, int]:
    diseases, priors, symptom_map = load_data()

    candidates = dict(priors)
    asked = set()
    cluster_strength = {c: 0.0 for c in CLUSTERS}
    scarcity_boosts = compute_scarcity_boosts(symptom_map, list(diseases.keys()))
    evidence_hits_by_disease = defaultdict(int)
    answered_with_lr = 0

    steps = 0
    finalized = False
    while steps < max_steps:
        sorted_c = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
        top_id, _ = sorted_c[0]
        confidence, _gap = calculate_confidence(candidates, diseases)
        req_hits_top = dynamic_required_hits(symptom_map, top_id)
        hits_top = evidence_hits_by_disease.get(top_id, 0)
        top_posterior = max(candidates.values()) if candidates else 0.0

        if hits_top >= req_hits_top and top_posterior >= EARLY_FINALIZE_TOPP:
            finalized = True
            break
        if confidence >= SUCCESS_CONFIDENCE and answered_with_lr >= MIN_EVIDENCE_ANSWERS:
            finalized = True
            break

        next_syms = select_next_symptoms(
            candidates,
            symptom_map,
            asked,
            cluster_strength=cluster_strength,
            scarcity_boosts=scarcity_boosts,
        )
        if not next_syms:
            break
        sym = pick_target_symptom(next_syms, target_id, symptom_map)
        if not sym:
            break

        asked.add(sym)
        cl = categorize_symptom(sym)
        cluster_strength[cl] = min(0.8, cluster_strength.get(cl, 0.0) + 0.3)

        did_map = symptom_map.get(sym, {})
        has_any_lr = False
        for d_id, vals in did_map.items():
            if vals.get("lr_pos") is not None:
                evidence_hits_by_disease[d_id] += 1
                has_any_lr = True
        if has_any_lr:
            answered_with_lr += 1

        candidates = update_posteriors_positive(candidates, sym, symptom_map, cluster_strength, scarcity_boosts)
        steps += 1

    sorted_c = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    top_id, top_p = sorted_c[0]
    req_hits_top = dynamic_required_hits(symptom_map, top_id)
    hits_top = evidence_hits_by_disease.get(top_id, 0)

    return finalized, steps, diseases[top_id]["name"], float(top_p), hits_top, req_hits_top


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max_steps", type=int, default=6)
    parser.add_argument("--min_evidence", type=int, default=2, help="Skip diseases with fewer than this many evidence-backed symptoms")
    parser.add_argument("--only", type=str, default="", help="Comma-separated disease names to test")
    parser.add_argument("--list", action="store_true", help="List each disease with its evidence-backed symptoms and exit")
    args = parser.parse_args()

    if args.list:
        list_disease_symptoms()
        return

    diseases, _priors, symptom_map = load_data()
    name_to_id = {info["name"].lower(): did for did, info in diseases.items()}

    targets = []
    if args.only:
        for n in [s.strip().lower() for s in args.only.split(",") if s.strip()]:
            did = name_to_id.get(n)
            if did is not None:
                targets.append(did)
    else:
        targets = list(diseases.keys())

    tested = 0
    successes = 0
    print("\nAuto-test summary (max steps = %d):" % args.max_steps)
    print("Disease | Steps | Finalized | TopDisease | TopP | Hits/Req")

    for did in targets:
        n_evid = count_evidence_symptoms_for_disease(symptom_map, did)
        if n_evid < args.min_evidence:
            continue
        tested += 1
        finalized, steps, top_name, top_p, hits, req = simulate_target(did, args.max_steps)
        success = finalized and steps <= args.max_steps
        if success:
            successes += 1
        print(f"{diseases[did]['name']} | {steps} | {str(finalized)} | {top_name} | {top_p:.3f} | {hits}/{req}")

    print(f"\nSuccess: {successes}/{tested} (skipped diseases with <{args.min_evidence} evidence-backed symptoms)")


if __name__ == "__main__":
    main()
