#!/usr/bin/env python3
import sqlite3
from math import log2
import math
import sys
from collections import defaultdict
import argparse

# disambiguate and add more features.
# choose more realistic numbers.

# Success criteria configuration
SUCCESS_CONFIDENCE = 0.9  # stop when confidence >= this (after evidence-based Qs)
MIN_EVIDENCE_ANSWERS = 3  # global minimum answers with any LR (kept as a floor)
EARLY_FINALIZE_TOPP = 0.55  # if enough per-disease evidence hits and top posterior >= this, finalize early

# Penalize diseases that lack LR evidence for selected symptoms (decays over steps)
COVERAGE_PENALTY = 0.9  # multiply probability by this if a selected symptom has no LR for that disease

# Dynamic cluster weighting (amplifies contributions of context-relevant symptoms)
CLUSTER_BOOST_PER_HIT = 0.3   # how much to add when a symptom from a cluster is selected
CLUSTER_BOOST_MAX = 0.8       # cap on cumulative boost

# Scarcity and stage weighting (boost contributions when disease has few evidence symptoms and as user converges)
SCARCITY_WEIGHT = 0.6
SCARCITY_BOOST_MAX = 0.8
STAGE_BOOST_MAX = 0.6
ALPHA_CAP = 3.0  # cap on LR exponent multiplier 1+boosts

# Lay explanations for common symptoms (fallback to a generic formatter if missing)
LAY_EXPLANATIONS = {
    "Fever": "Temperature 38°C (100.4°F) or higher.",
    "Low-grade fever": "Mildly elevated temperature, usually under 38.5°C (101.3°F).",
    "Cough": "Repeated forceful exhalations; can be dry or with mucus.",
    "Rhinorrhea (runny nose)": "Runny nose with clear or colored mucus.",
    "Nasal congestion": "Stuffy or blocked nose; breathing through mouth.",
    "Sore throat": "Pain or scratchiness in the throat, worse when swallowing.",
    "Ear pain": "Pain in or around the ear; child may be fussy or cry.",
    "Ear pulling/tugging": "Child pulls on the ear, often due to discomfort.",
    "Otorrhea (ear discharge)": "Fluid or pus draining from the ear canal.",
    "Wheezing": "High-pitched whistling sound when breathing out.",
    "Dyspnea (shortness of breath)": "Hard to catch breath; breathing feels labored.",
    "Chest tightness": "Sensation of pressure or tight feeling in the chest.",
    "Tachypnea (rapid breathing)": "Breathing faster than usual for age.",
    "Chest retractions": "Skin pulls in between ribs/neck when breathing (working hard).",
    "Hypoxemia (low oxygen)": "Low blood oxygen; may look bluish or very tired.",
    "Pleuritic chest pain": "Sharp chest pain that worsens with deep breaths or cough.",
    "Crackles on auscultation": "Bubbly popping sounds heard by a clinician with a stethoscope.",
    "Myalgia (muscle aches)": "General body aches and pains.",
    "Headache": "Pain in the head or face area.",
    "Malaise/fatigue": "Low energy; feeling unwell or unusually tired.",
    "Barking cough": "Harsh, seal-like cough sound.",
    "Stridor": "High-pitched noisy breathing, especially when inhaling.",
    "Hoarseness": "Raspy or weak voice.",
    "Tonsillar exudate": "White patches or pus on the tonsils.",
    "Tender anterior cervical lymph nodes": "Sore, enlarged glands in the front of the neck.",
    "Nasal discharge (purulent)": "Thick yellow/green mucus from the nose.",
    "Persistent cough (>10 days)": "Cough lasting longer than 10 days.",
    "Vomiting": "Throwing up.",
    "Diarrhea": "Loose or watery stools more often than usual.",
    "Abdominal pain": "Stomach ache or tummy pain.",
    "Decreased urination": "Fewer wet diapers or bathroom trips than usual.",
    "Signs of dehydration": "Dry mouth, sunken eyes, few tears, very tired.",
    "Dysuria (painful urination)": "Pain or burning when peeing.",
    "Urinary frequency": "Needing to pee more often than usual.",
    "Urinary urgency": "Strong sudden need to pee.",
    "Abdominal/suprapubic pain": "Pain in the lower belly above the pubic bone.",
    "Eye redness": "Red or pink eyes.",
    "Eye discharge": "Goopy or crusty drainage from the eyes.",
    "Itchy eyes": "Eyes that feel itchy or irritated.",
    "Eyelids stuck shut on waking": "Eyelids glued by crust in the morning.",
    "Oral ulcers": "Small painful sores inside the mouth.",
    "Vesicular rash on hands": "Small blisters on the hands.",
    "Vesicular rash on feet": "Small blisters on the feet.",
    "Pruritus (itching)": "Skin that feels itchy.",
    "Eczematous rash": "Dry, scaly, itchy patches of skin.",
    "Xerosis (dry skin)": "Very dry skin.",
    "Flexural involvement": "Rash in elbow/knee folds, neck, ankles.",
    "Honey-colored crusts": "Yellowish crusts on red skin, often on face.",
    "Erythema (redness)": "Redness of the skin.",
    "Facial rash (slapped-cheek)": "Bright red cheeks, like a slap mark.",
    "Lacy reticular rash (trunk)": "Lacy, net-like rash on the body.",
    "High fever (3-5 days)": "High temperature lasting 3 to 5 days.",
    "Maculopapular rash (after fever resolves)": "Flat and bumpy rash appearing after fever goes away.",
    "Pruritic vesicular rash": "Itchy blisters on the skin.",
    "Lesions in different stages": "New blisters, scabs, and spots all at once.",
    "Ear canal edema/erythema": "Swollen, red ear canal.",
    "Ear pain (worse with tragal pressure)": "Ear hurts when you press the small flap in front of the ear.",
    "Sneezing": "Sudden air bursts through nose/mouth.",
    "Itchy eyes": "Eyes that feel itchy or irritated.",
}

CLUSTERS = ["respiratory", "ent", "gi", "gu", "skin", "eye", "general"]


def categorize_symptom(symptom: str) -> str:
    s = symptom.lower()
    if any(k in s for k in ["wheez", "tachypnea", "retraction", "hypox", "cough", "stridor", "barking", "pleuritic", "crackles", "dyspnea", "chest"]):
        return "respiratory"
    if any(k in s for k in ["ear", "throat", "tonsil", "otorrhea", "sore throat", "hoarseness", "sinus", "nasal"]):
        return "ent"
    if any(k in s for k in ["vomit", "diarr", "abdominal", "suprapubic", "dehydration"]):
        return "gi"
    if any(k in s for k in ["dysuria", "urinary", "pee", "urination"]):
        return "gu"
    if any(k in s for k in ["rash", "itch", "eczema", "vesicular", "erythema", "crust", "skin", "maculopapular"]):
        return "skin"
    if any(k in s for k in ["eye", "conjunct", "eyelid"]):
        return "eye"
    return "general"


def explain_symptom(symptom: str) -> str:
    if symptom in LAY_EXPLANATIONS:
        return LAY_EXPLANATIONS[symptom]
    if "(" in symptom and ")" in symptom:
        inner = symptom.split("(", 1)[1].rsplit(")", 1)[0]
        return inner.strip().capitalize() + "."
    return f"Plain terms: {symptom.lower()}."


def count_evidence_symptoms_for_disease(symptom_map: dict, disease_id: int) -> int:
    count = 0
    for sym, did_map in symptom_map.items():
        if disease_id in did_map and did_map[disease_id].get("lr_pos") is not None:
            count += 1
    return count


def dynamic_required_hits(symptom_map: dict, disease_id: int) -> int:
    n = count_evidence_symptoms_for_disease(symptom_map, disease_id)
    # Require roughly 40% of available positive-evidence symptoms, clamped between 2 and 5
    required = math.ceil(0.4 * n)
    return max(2, min(5, required))


def load_data(db_path="pediatric.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, name, triage_severity, description
        FROM diseases
        """
    )
    disease_rows = cur.fetchall()
    if not disease_rows:
        conn.close()
        raise sqlite3.OperationalError("No diseases found. Load data first.")

    diseases = {
        row[0]: {
            "name": row[1],
            "triage_severity": float(row[2]) if row[2] is not None else 1.0,
            "description": row[3] or "",
        }
        for row in disease_rows
    }

    cur.execute(
        """
        SELECT disease_id, prevalence FROM disease_priors
        """
    )
    priors = {row[0]: float(row[1]) for row in cur.fetchall() if row[1] is not None}
    if priors:
        total_prior = sum(priors.values()) or 1.0
        priors = {d: p / total_prior for d, p in priors.items() if d in diseases}
    else:
        uniform = 1.0 / len(diseases)
        priors = {d: uniform for d in diseases.keys()}

    cur.execute(
        """
        SELECT dpe.disease_id, p.name, dpe.lr_pos, dpe.lr_neg
        FROM disease_phenotype_evidence dpe
        JOIN phenotypes p ON p.id = dpe.phenotype_id
        """
    )
    symptom_map = {}
    for did, symptom, lr_pos, lr_neg in cur.fetchall():
        if did not in diseases:
            continue
        info = symptom_map.setdefault(symptom, {})
        prev = info.get(did)
        new_lr_pos = float(lr_pos) if lr_pos is not None else None
        new_lr_neg = float(lr_neg) if lr_neg is not None else None
        if prev is None:
            info[did] = {"lr_pos": new_lr_pos, "lr_neg": new_lr_neg}
        else:
            if prev.get("lr_pos") is None and new_lr_pos is not None:
                prev["lr_pos"] = new_lr_pos
            if prev.get("lr_neg") is None and new_lr_neg is not None:
                prev["lr_neg"] = new_lr_neg

    conn.close()
    return diseases, priors, symptom_map


def compute_scarcity_boosts(symptom_map: dict, disease_ids: list[int]) -> dict[int, float]:
    counts = {d: count_evidence_symptoms_for_disease(symptom_map, d) for d in disease_ids}
    nonzero = [max(1, c) for c in counts.values()] or [1]
    # Use median as reference
    sorted_counts = sorted(nonzero)
    m = sorted_counts[len(sorted_counts)//2]
    boosts = {}
    for d, c in counts.items():
        c = max(1, c)
        raw = (m / c) - 1.0  # >0 if fewer than median
        boost = max(0.0, min(SCARCITY_BOOST_MAX, SCARCITY_WEIGHT * raw))
        boosts[d] = boost
    return boosts


def compute_entropy(p_yes):
    if p_yes <= 0 or p_yes >= 1:
        return 0.0
    return -p_yes * log2(p_yes) - (1 - p_yes) * log2(1 - p_yes)


def positive_score(symptom, did_map, candidates, min_lr_pos: float = 1.0, cluster_strength=None, scarcity_boosts=None):
    score = 0.0
    has_pos = False
    for d, post in candidates.items():
        lrp = did_map.get(d, {}).get("lr_pos")
        if lrp is not None and lrp >= min_lr_pos:
            has_pos = True
            scarcity = (scarcity_boosts or {}).get(d, 0.0)
            mult = 1.0 + scarcity
            score += post * max(0.0, math.log(lrp)) * mult
    if not has_pos:
        return 0.0
    if cluster_strength is not None:
        cluster = categorize_symptom(symptom)
        score *= (1.0 + 0.5 * min(CLUSTER_BOOST_MAX, cluster_strength.get(cluster, 0.0)))
    return score


def select_next_symptoms(candidates, symptom_map, asked, top_n=5, cluster_strength=None, scarcity_boosts=None):
    infos = []
    for symptom, did_map in symptom_map.items():
        if symptom in asked:
            continue
        gain = positive_score(symptom, did_map, candidates, cluster_strength=cluster_strength, scarcity_boosts=scarcity_boosts)
        if gain > 0:
            infos.append((symptom, gain))
    infos.sort(key=lambda x: x[1], reverse=True)
    return [symptom for symptom, _ in infos[:top_n]]


def update_posteriors_positive(candidates, symptom, symptom_map, cluster_strength, scarcity_boosts):
    updated = {}
    cluster = categorize_symptom(symptom)
    cluster_boost = min(CLUSTER_BOOST_MAX, cluster_strength.get(cluster, 0.0))
    for d, post in candidates.items():
        did_map = symptom_map.get(symptom, {})
        lr_pos = did_map.get(d, {}).get("lr_pos")
        # coverage penalty if missing LR
        if lr_pos is None:
            post *= COVERAGE_PENALTY
            lr = 1.0
        else:
            scarcity = scarcity_boosts.get(d, 0.0) if scarcity_boosts else 0.0
            stage = STAGE_BOOST_MAX * candidates.get(d, 0.0)
            alpha_extra = min(ALPHA_CAP - 1.0, cluster_boost + scarcity + stage)
            lr = max(1e-9, lr_pos) ** (1.0 + alpha_extra)
        post = max(min(post, 1 - 1e-12), 1e-12)
        odds = post / (1 - post)
        new_odds = odds * lr
        new_p = new_odds / (1 + new_odds)
        updated[d] = new_p
    total = sum(updated.values())
    return candidates if total == 0 else {d: val / total for d, val in updated.items()}


def calculate_confidence(candidates, diseases):
    sorted_c = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    if not sorted_c:
        return 0.0, 0.0
    top_prob = sorted_c[0][1]
    second_prob = sorted_c[1][1] if len(sorted_c) > 1 else 0.0
    confidence = top_prob * (1 + (top_prob - second_prob))
    top_disease = diseases[sorted_c[0][0]]
    severity_factor = top_disease.get("triage_severity", 1.0)
    return min(confidence * severity_factor, 1.0), top_prob - second_prob


def preview_recommendations(diseases, priors, symptom_map, top_n=10):
    candidates = dict(priors)
    asked = set()
    cluster_strength = {c: 0.0 for c in CLUSTERS}
    scarcity_boosts = compute_scarcity_boosts(symptom_map, list(diseases.keys()))
    recs = select_next_symptoms(candidates, symptom_map, asked, top_n=top_n, cluster_strength=cluster_strength, scarcity_boosts=scarcity_boosts)
    print("Recommended next symptoms (with plain-language help):")
    for i, sym in enumerate(recs, 1):
        did_map = symptom_map.get(sym, {})
        num_with_lr = sum(1 for v in did_map.values() if (v.get('lr_pos') is not None))
        print(f"{i}. {sym}")
        print(f"   What it means: {explain_symptom(sym)}")
        print(f"   Positive LR coverage: {num_with_lr} diseases")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", type=int, default=0, help="Show top-N recommended symptoms and exit")
    args = parser.parse_args()

    try:
        diseases, priors, symptom_map = load_data()
    except sqlite3.OperationalError as e:
        print(f"Error loading database: {e}")
        sys.exit(1)

    if args.preview:
        preview_recommendations(diseases, priors, symptom_map, top_n=args.preview)
        return

    candidates = dict(priors)

    print("\nPediatric Disease Diagnosis System")
    print("----------------------------------")
    print("Select symptoms the child HAS. No need to confirm negatives.")

    asked = set()
    answered_with_lr = 0
    evidence_hits_by_disease = defaultdict(int)
    cluster_strength = {c: 0.0 for c in CLUSTERS}
    scarcity_boosts = compute_scarcity_boosts(symptom_map, list(diseases.keys()))
    consecutive_low_gain = 0

    while True:
        sorted_c = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
        top_id, top_prob = sorted_c[0]
        remaining = [d for d, p in sorted_c if p > 0.01]

        print("\nCurrent top diagnoses:")
        for did, prob in sorted_c[:3]:
            disease_info = diseases[did]
            print(f"{disease_info['name']} (P={prob:.3f})")
            print(f"  Triage severity: {disease_info['triage_severity']}")
            if disease_info['description']:
                print(f"  Description: {disease_info['description']}")

        confidence, gap = calculate_confidence(candidates, diseases)
        req_hits_top = dynamic_required_hits(symptom_map, top_id)
        hits_top = evidence_hits_by_disease.get(top_id, 0)
        print(f"Current confidence: {confidence:.2f} (gap={gap:.2f}), answered with evidence: {answered_with_lr}, top disease hits {hits_top}/{req_hits_top}")

        top_posterior = max(candidates.values()) if candidates else 0.0
        if hits_top >= req_hits_top and top_posterior >= EARLY_FINALIZE_TOPP:
            print("\nEarly finalize criteria met (per-disease).")
            break

        if (confidence >= SUCCESS_CONFIDENCE and answered_with_lr >= MIN_EVIDENCE_ANSWERS) or len(remaining) <= 2:
            print("\nStopping criteria met.")
            break

        next_syms = select_next_symptoms(candidates, symptom_map, asked, top_n=15, cluster_strength=cluster_strength, scarcity_boosts=scarcity_boosts)
        if not next_syms:
            print("\nNo further high-value symptoms remain. Finalizing.")
            break

        print("\nNext symptom options (choose one that IS present):")
        for i, sym in enumerate(next_syms, 1):
            did_map = symptom_map.get(sym, {})
            num_with_lr = sum(1 for v in did_map.values() if (v.get('lr_pos') is not None))
            print(f"{i}. {sym}")
            print(f"   What it means: {explain_symptom(sym)}")
            print(f"   Positive LR coverage: {num_with_lr} diseases")

        choice = input(f"\nChoose symptom 1-{len(next_syms)} that the child HAS (or '0' for none, 's' to skip, 'q' to quit): ")
        if choice.lower() == 'q':
            break
        if choice.lower() == 's':
            # Skip: just mark symptoms as asked and show new options (don't count as low gain)
            for sym in next_syms:
                asked.add(sym)
            continue
        if choice == '0' or choice.lower() in ('none', 'n'):
            # Mark all proposed as asked and continue (counts as low gain since no symptom selected)
            for sym in next_syms:
                asked.add(sym)
            consecutive_low_gain += 1
            if consecutive_low_gain >= 2:
                print("\nInsufficient progress. Finalizing.")
                break
            continue
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(next_syms):
                raise ValueError
        except ValueError:
            print("Invalid selection; try again.")
            continue

        symptom = next_syms[idx]
        asked.add(symptom)

        cl = categorize_symptom(symptom)
        cluster_strength[cl] = min(CLUSTER_BOOST_MAX, cluster_strength.get(cl, 0.0) + CLUSTER_BOOST_PER_HIT)

        did_map = symptom_map.get(symptom, {})
        has_any_lr = False
        for d_id, vals in did_map.items():
            if vals.get('lr_pos') is not None:
                evidence_hits_by_disease[d_id] += 1
                has_any_lr = True
        if has_any_lr:
            answered_with_lr += 1

        prev_top = max(candidates.values()) if candidates else 0.0
        candidates = update_posteriors_positive(candidates, symptom, symptom_map, cluster_strength, scarcity_boosts)
        new_top = max(candidates.values()) if candidates else 0.0
        if new_top - prev_top < 0.05:
            consecutive_low_gain += 1
        else:
            consecutive_low_gain = 0

if __name__ == "__main__":
    main()
