#!/usr/bin/env python3
"""
Improved Inference Script for Pediatric Diagnosis
Better handles common diseases and improves robustness
"""

import sqlite3
from math import log2
import math
import sys
import os
from collections import defaultdict
import argparse

# Success criteria configuration - improved for common diseases
SUCCESS_CONFIDENCE = 0.85  # Lowered from 0.9 to be more lenient
MIN_EVIDENCE_ANSWERS = 2   # Lowered from 3 to allow faster convergence
EARLY_FINALIZE_TOPP = 0.50  # Lowered from 0.55 for common diseases
MAX_STEPS = 20  # Increased from implicit 6-15 to allow more exploration

# Penalize diseases that lack LR evidence for selected symptoms (less aggressive)
COVERAGE_PENALTY = 0.95  # Less aggressive penalty (was 0.9)

# Dynamic cluster weighting (amplifies contributions of context-relevant symptoms)
CLUSTER_BOOST_PER_HIT = 0.25   # Slightly reduced
CLUSTER_BOOST_MAX = 0.7        # Reduced cap

# Scarcity and stage weighting - adjusted for better common disease handling
SCARCITY_WEIGHT = 0.4  # Reduced to not over-penalize common diseases
SCARCITY_BOOST_MAX = 0.6
STAGE_BOOST_MAX = 0.5
ALPHA_CAP = 2.5  # Reduced cap to prevent over-boosting rare diseases

# Common disease boost - NEW: boost common diseases based on prior
COMMON_DISEASE_THRESHOLD = 0.01  # Diseases with prior >= 1% are "common"
COMMON_DISEASE_BOOST = 0.15  # Boost common disease posteriors

# Lay explanations (same as before)
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


def load_data(db_path: str = "pediatric.db"):
    # Handle PyInstaller executable case
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_dir = sys._MEIPASS
        exe_dir = os.path.dirname(sys.executable)
        
        # Try multiple locations for database
        possible_paths = [
            os.path.join(base_dir, "pediatric.db"),  # Bundled with executable
            os.path.join(exe_dir, "pediatric.db"),   # Same directory as executable
            os.path.join(os.getcwd(), "pediatric.db"),  # Current working directory
            db_path  # Original path
        ]
        
        # Find first existing database
        for path in possible_paths:
            if os.path.exists(path):
                db_path = path
                break
        else:
            # If not found, use original path and let sqlite3 handle the error
            pass
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    diseases = {}
    cur.execute("SELECT id, name, triage_severity, description FROM diseases")
    for row in cur.fetchall():
        diseases[row[0]] = {
            "name": row[1],
            "triage_severity": row[2] if row[2] is not None else 1.0,
            "description": row[3] if row[3] else ""
        }
    
    priors = {}
    cur.execute("SELECT disease_id, prevalence FROM disease_priors")
    for row in cur.fetchall():
        priors[row[0]] = row[1] if row[1] is not None else 0.0
    
    # Normalize priors
    total = sum(priors.values())
    if total > 0:
        priors = {k: v / total for k, v in priors.items()}
    
    symptom_map = defaultdict(dict)
    cur.execute("""
        SELECT dpe.disease_id, p.name, dpe.lr_pos, dpe.lr_neg, dpe.sensitivity, dpe.specificity
        FROM disease_phenotype_evidence dpe
        JOIN phenotypes p ON p.id = dpe.phenotype_id
    """)
    for row in cur.fetchall():
        disease_id, symptom, lr_pos, lr_neg, sens, spec = row
        symptom_map[symptom][disease_id] = {
            "lr_pos": lr_pos,
            "lr_neg": lr_neg,
            "sensitivity": sens,
            "specificity": spec
        }
    
    conn.close()
    return diseases, priors, dict(symptom_map)


def compute_scarcity_boosts(symptom_map: dict, disease_ids: list) -> dict:
    boosts = {}
    for did in disease_ids:
        count = sum(1 for sym_map in symptom_map.values() if did in sym_map and sym_map[did].get("lr_pos") is not None)
        if count < 5:
            boosts[did] = SCARCITY_WEIGHT * (5 - count) / 5.0
        else:
            boosts[did] = 0.0
    return boosts


def dynamic_required_hits(symptom_map: dict, disease_id: int) -> int:
    count = sum(1 for sym_map in symptom_map.values() if disease_id in sym_map and sym_map[disease_id].get("lr_pos") is not None)
    if count <= 2:
        return 1
    elif count <= 5:
        return 2
    else:
        return 3


def improved_positive_score(
    symptom: str,
    did_map: dict,
    candidates: dict,
    priors: dict,
    min_lr_pos: float = 1.0,
    cluster_strength: dict = None,
    scarcity_boosts: dict = None
) -> float:
    """
    Improved symptom scoring that:
    1. Better prioritizes common disease symptoms
    2. Considers disease prevalence/prior
    3. Balances information gain with accessibility
    """
    score = 0.0
    has_pos = False
    
    for d, post in candidates.items():
        lrp = did_map.get(d, {}).get("lr_pos")
        if lrp is not None and lrp >= min_lr_pos:
            has_pos = True
            
            # Base score: posterior-weighted information gain
            base_gain = post * max(0.0, math.log(lrp))
            
            # Common disease boost: prioritize symptoms for common diseases
            prior = priors.get(d, 0.0)
            common_boost = 1.0
            if prior >= COMMON_DISEASE_THRESHOLD:
                common_boost = 1.0 + COMMON_DISEASE_BOOST
            
            # Scarcity boost (reduced)
            scarcity = (scarcity_boosts or {}).get(d, 0.0)
            scarcity_mult = 1.0 + scarcity * 0.5  # Reduced impact
            
            # Combined score
            score += base_gain * common_boost * scarcity_mult
    
    if not has_pos:
        return 0.0
    
    # Cluster boost (reduced)
    if cluster_strength is not None:
        cluster = categorize_symptom(symptom)
        cluster_mult = 1.0 + 0.3 * min(CLUSTER_BOOST_MAX, cluster_strength.get(cluster, 0.0))
        score *= cluster_mult
    
    return score


def select_next_symptoms(
    candidates: dict,
    symptom_map: dict,
    asked: set,
    priors: dict,
    top_n: int = 15,
    cluster_strength: dict = None,
    scarcity_boosts: dict = None
) -> list:
    """
    Improved symptom selection that better handles common diseases
    """
    infos = []
    for symptom, did_map in symptom_map.items():
        if symptom in asked:
            continue
        gain = improved_positive_score(
            symptom, did_map, candidates, priors,
            cluster_strength=cluster_strength,
            scarcity_boosts=scarcity_boosts
        )
        if gain > 0:
            infos.append((symptom, gain))
    
    infos.sort(key=lambda x: x[1], reverse=True)
    return [symptom for symptom, _ in infos[:top_n]]


def update_posteriors_positive(
    candidates: dict,
    symptom: str,
    symptom_map: dict,
    priors: dict,
    cluster_strength: dict,
    scarcity_boosts: dict
) -> dict:
    """
    Improved posterior update that:
    1. Less aggressive coverage penalty
    2. Better handling of common diseases
    3. More balanced boosting
    """
    updated = {}
    cluster = categorize_symptom(symptom)
    cluster_boost = min(CLUSTER_BOOST_MAX, cluster_strength.get(cluster, 0.0))
    
    for d, post in candidates.items():
        did_map = symptom_map.get(symptom, {})
        lr_pos = did_map.get(d, {}).get("lr_pos")
        
        # Coverage penalty (less aggressive)
        if lr_pos is None:
            post *= COVERAGE_PENALTY
            lr = 1.0
        else:
            # Reduced boosting to prevent over-weighting rare diseases
            scarcity = scarcity_boosts.get(d, 0.0) if scarcity_boosts else 0.0
            stage = STAGE_BOOST_MAX * min(candidates.get(d, 0.0), 0.5)  # Cap stage boost
            
            # Common disease boost
            prior = priors.get(d, 0.0)
            common_boost = 0.0
            if prior >= COMMON_DISEASE_THRESHOLD:
                common_boost = COMMON_DISEASE_BOOST * 0.5  # Moderate boost
            
            alpha_extra = min(ALPHA_CAP - 1.0, cluster_boost + scarcity * 0.5 + stage + common_boost)
            lr = max(1e-9, lr_pos) ** (1.0 + alpha_extra)
        
        post = max(min(post, 1 - 1e-12), 1e-12)
        odds = post / (1 - post)
        new_odds = odds * lr
        new_p = new_odds / (1 + new_odds)
        updated[d] = new_p
    
    total = sum(updated.values())
    return candidates if total == 0 else {d: val / total for d, val in updated.items()}


def calculate_confidence(candidates: dict, diseases: dict) -> tuple:
    """
    Improved confidence calculation that's more lenient
    """
    sorted_c = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    if not sorted_c:
        return 0.0, 0.0
    
    top_prob = sorted_c[0][1]
    second_prob = sorted_c[1][1] if len(sorted_c) > 1 else 0.0
    gap = top_prob - second_prob
    
    # More lenient confidence calculation
    confidence = top_prob * (1 + gap * 0.8)  # Reduced gap multiplier
    
    top_disease = diseases[sorted_c[0][0]]
    severity_factor = top_disease.get("triage_severity", 1.0)
    
    return min(confidence * severity_factor, 1.0), gap


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", type=int, default=0, help="Show top-N recommended symptoms and exit")
    parser.add_argument("--db", type=str, default="pediatric.db", help="Database file path")
    args = parser.parse_args()

    try:
        diseases, priors, symptom_map = load_data(args.db)
    except sqlite3.OperationalError as e:
        print(f"Error loading database: {e}")
        sys.exit(1)

    if args.preview:
        candidates = dict(priors)
        asked = set()
        cluster_strength = {c: 0.0 for c in CLUSTERS}
        scarcity_boosts = compute_scarcity_boosts(symptom_map, list(diseases.keys()))
        recs = select_next_symptoms(candidates, symptom_map, asked, priors, top_n=args.preview, cluster_strength=cluster_strength, scarcity_boosts=scarcity_boosts)
        print("Recommended next symptoms (with plain-language help):")
        for i, sym in enumerate(recs, 1):
            did_map = symptom_map.get(sym, {})
            num_with_lr = sum(1 for v in did_map.values() if (v.get('lr_pos') is not None))
            print(f"{i}. {sym}")
            print(f"   What it means: {explain_symptom(sym)}")
            print(f"   Positive LR coverage: {num_with_lr} diseases")
        return

    candidates = dict(priors)

    print("\nPediatric Disease Diagnosis System (Improved)")
    print("=" * 50)
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
        
        # Improved convergence criteria
        if hits_top >= req_hits_top and top_posterior >= EARLY_FINALIZE_TOPP:
            print("\nEarly finalize criteria met (per-disease).")
            break

        if (confidence >= SUCCESS_CONFIDENCE and answered_with_lr >= MIN_EVIDENCE_ANSWERS) or len(remaining) <= 2:
            print("\nStopping criteria met.")
            break

        if len(asked) >= MAX_STEPS:
            print(f"\nMaximum steps ({MAX_STEPS}) reached. Finalizing.")
            break

        next_syms = select_next_symptoms(
            candidates, symptom_map, asked, priors,
            top_n=15, cluster_strength=cluster_strength, scarcity_boosts=scarcity_boosts
        )
        
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

        try:
            choice = input("\nChoose symptom 1-{} that the child HAS (or '0' for none, 's' to skip, 'q' to quit): ".format(len(next_syms))).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if choice.lower() == 'q':
            break
        if choice == '0':
            consecutive_low_gain += 1
            if consecutive_low_gain >= 3:
                print("\nInsufficient progress. Finalizing.")
                break
            continue
        if choice.lower() == 's':
            # Skip doesn't increment low gain counter
            continue

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(next_syms):
                symptom = next_syms[idx]
            else:
                print("Invalid choice.")
                continue
        except ValueError:
            print("Invalid input.")
            continue

        asked.add(symptom)
        cl = categorize_symptom(symptom)
        cluster_strength[cl] = min(CLUSTER_BOOST_MAX, cluster_strength.get(cl, 0.0) + CLUSTER_BOOST_PER_HIT)

        did_map = symptom_map.get(symptom, {})
        has_any_lr = False
        for d_id, vals in did_map.items():
            if vals.get("lr_pos") is not None:
                evidence_hits_by_disease[d_id] += 1
                has_any_lr = True
        if has_any_lr:
            answered_with_lr += 1

        prev_top = max(candidates.values()) if candidates else 0.0
        candidates = update_posteriors_positive(candidates, symptom, symptom_map, priors, cluster_strength, scarcity_boosts)
        new_top = max(candidates.values()) if candidates else 0.0
        
        if new_top - prev_top < 0.05:
            consecutive_low_gain += 1
        else:
            consecutive_low_gain = 0

        if consecutive_low_gain >= 3:
            print("\nInsufficient progress. Finalizing.")
            break

    sorted_c = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    print("\n" + "=" * 50)
    print("Final Diagnosis:")
    for did, prob in sorted_c[:5]:
        disease_info = diseases[did]
        print(f"{disease_info['name']}: {prob:.1%}")


if __name__ == "__main__":
    main()

