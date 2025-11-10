#!/usr/bin/env python3
"""
Rigorous Autotest Script for Pediatric Diagnosis Inference System
Uses ML techniques for test case generation, validation, and anomaly detection
"""

import argparse
import sqlite3
import json
import math
from collections import defaultdict, Counter
from typing import List, Tuple, Dict, Set, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import random
import numpy as np
from scipy import stats

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


@dataclass
class TestResult:
    """Structured test result"""
    disease_id: int
    disease_name: str
    test_scenario: str
    converged: bool
    steps: int
    final_top_disease: str
    final_top_prob: float
    target_prob_at_end: float
    confidence: float
    evidence_hits: int
    required_hits: int
    symptom_path: List[str]
    posterior_trajectory: List[float]
    convergence_reason: str
    errors: List[str]
    warnings: List[str]


@dataclass
class DiseaseMetrics:
    """Aggregated metrics for a disease"""
    disease_id: int
    disease_name: str
    total_tests: int
    convergence_rate: float
    avg_steps: float
    avg_confidence: float
    avg_final_prob: float
    min_steps: int
    max_steps: int
    symptom_coverage: float
    evidence_symptom_count: int
    failure_modes: Dict[str, int]


class MLTestGenerator:
    """ML-based test case generator"""
    
    def __init__(self, diseases: Dict, symptom_map: Dict, target_id: int):
        self.diseases = diseases
        self.symptom_map = symptom_map
        self.target_id = target_id
        self.target_symptoms = self._get_target_symptoms()
        self.competitor_symptoms = self._get_competitor_symptoms()
    
    def _get_target_symptoms(self) -> List[Tuple[str, float]]:
        """Get symptoms with LR+ for target disease, sorted by LR+"""
        symptoms = []
        for sym, did_map in self.symptom_map.items():
            if self.target_id in did_map:
                lr_pos = did_map[self.target_id].get("lr_pos")
                if lr_pos and lr_pos > 1.0:
                    symptoms.append((sym, lr_pos))
        return sorted(symptoms, key=lambda x: x[1], reverse=True)
    
    def _get_competitor_symptoms(self) -> List[str]:
        """Get symptoms that favor competitor diseases"""
        competitor_syms = []
        for sym, did_map in self.symptom_map.items():
            max_lr = 0.0
            target_lr = did_map.get(self.target_id, {}).get("lr_pos", 0.0) or 0.0
            for did, vals in did_map.items():
                if did != self.target_id:
                    lr = vals.get("lr_pos", 0.0) or 0.0
                    if lr > max_lr:
                        max_lr = lr
            if max_lr > target_lr * 1.5:  # Strongly favors competitor
                competitor_syms.append(sym)
        return competitor_syms
    
    def generate_optimal_path(self) -> List[str]:
        """Generate optimal symptom path (highest LR+ symptoms first)"""
        return [sym for sym, _ in self.target_symptoms[:10]]
    
    def generate_suboptimal_path(self, noise_level: float = 0.3) -> List[str]:
        """Generate suboptimal path with some noise"""
        path = []
        target_syms = [sym for sym, _ in self.target_symptoms]
        competitor_syms = self.competitor_symptoms[:5]
        
        for i in range(min(10, len(target_syms))):
            if random.random() < noise_level and competitor_syms:
                path.append(random.choice(competitor_syms))
            else:
                path.append(target_syms[i] if i < len(target_syms) else random.choice(target_syms))
        return path
    
    def generate_adversarial_path(self) -> List[str]:
        """Generate adversarial path (competitor symptoms first)"""
        path = []
        # Start with competitor symptoms
        path.extend(self.competitor_symptoms[:3])
        # Then add target symptoms
        path.extend([sym for sym, _ in self.target_symptoms[:7]])
        return path
    
    def generate_random_path(self, length: int = 10) -> List[str]:
        """Generate random valid symptom path"""
        all_symptoms = list(self.symptom_map.keys())
        return random.sample(all_symptoms, min(length, len(all_symptoms)))
    
    def generate_diverse_paths(self, n: int = 5) -> List[List[str]]:
        """Generate diverse test paths using clustering"""
        paths = []
        # Optimal
        paths.append(self.generate_optimal_path())
        # Suboptimal variants
        for _ in range(n - 1):
            noise = random.uniform(0.2, 0.5)
            paths.append(self.generate_suboptimal_path(noise_level=noise))
        return paths


class AnomalyDetector:
    """ML-based anomaly detection for test results"""
    
    def __init__(self):
        self.normal_ranges = {}
    
    def fit(self, results: List[TestResult]):
        """Learn normal ranges from results"""
        steps = [r.steps for r in results if r.converged]
        confidences = [r.confidence for r in results if r.converged]
        probs = [r.final_top_prob for r in results if r.converged]
        
        self.normal_ranges = {
            'steps': (np.mean(steps) - 2*np.std(steps), np.mean(steps) + 2*np.std(steps)),
            'confidence': (np.mean(confidences) - 2*np.std(confidences), np.mean(confidences) + 2*np.std(confidences)),
            'prob': (np.mean(probs) - 2*np.std(probs), np.mean(probs) + 2*np.std(probs)),
        }
    
    def detect_anomalies(self, result: TestResult) -> List[str]:
        """Detect anomalies in a test result"""
        anomalies = []
        
        if result.converged:
            if result.steps < self.normal_ranges['steps'][0] or result.steps > self.normal_ranges['steps'][1]:
                anomalies.append(f"Unusual step count: {result.steps}")
            if result.confidence < self.normal_ranges['confidence'][0]:
                anomalies.append(f"Low confidence: {result.confidence:.3f}")
            if result.final_top_prob < self.normal_ranges['prob'][0]:
                anomalies.append(f"Low final probability: {result.final_top_prob:.3f}")
        else:
            anomalies.append("Failed to converge")
        
        # Check for unusual posterior trajectories
        if len(result.posterior_trajectory) > 1:
            if result.posterior_trajectory[-1] < result.posterior_trajectory[0]:
                anomalies.append("Posterior decreased over time")
            if max(result.posterior_trajectory) - min(result.posterior_trajectory) > 0.5:
                anomalies.append("High posterior variance")
        
        return anomalies


def simulate_inference(
    target_id: int,
    symptom_path: List[str],
    max_steps: int = 15,
    db_path: str = "pediatric.db",
    scenario_name: str = "unknown"
) -> TestResult:
    """Simulate inference with a specific symptom path"""
    diseases, priors, symptom_map = load_data(db_path)
    
    candidates = dict(priors)
    asked = set()
    cluster_strength = {c: 0.0 for c in CLUSTERS}
    scarcity_boosts = compute_scarcity_boosts(symptom_map, list(diseases.keys()))
    evidence_hits_by_disease = defaultdict(int)
    answered_with_lr = 0
    
    symptom_sequence = []
    posterior_trajectory = [candidates.get(target_id, 0.0)]
    errors = []
    warnings = []
    convergence_reason = ""
    
    steps = 0
    finalized = False
    
    # Follow the provided symptom path
    for step in range(min(max_steps, len(symptom_path))):
        sym = symptom_path[step]
        
        if sym not in symptom_map:
            errors.append(f"Unknown symptom: {sym}")
            continue
        
        if sym in asked:
            warnings.append(f"Symptom {sym} already asked, skipping")
            continue
        
        asked.add(sym)
        symptom_sequence.append(sym)
        
        # Update cluster strength
        cl = categorize_symptom(sym)
        cluster_strength[cl] = min(0.8, cluster_strength.get(cl, 0.0) + 0.3)
        
        # Track evidence hits
        did_map = symptom_map.get(sym, {})
        has_any_lr = False
        for d_id, vals in did_map.items():
            if vals.get("lr_pos") is not None:
                evidence_hits_by_disease[d_id] += 1
                has_any_lr = True
        if has_any_lr:
            answered_with_lr += 1
        
        # Update posteriors
        prev_target_prob = candidates.get(target_id, 0.0)
        candidates = update_posteriors_positive(candidates, sym, symptom_map, cluster_strength, scarcity_boosts)
        new_target_prob = candidates.get(target_id, 0.0)
        posterior_trajectory.append(new_target_prob)
        
        # Check convergence
        sorted_c = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
        top_id, top_prob = sorted_c[0]
        confidence, gap = calculate_confidence(candidates, diseases)
        req_hits_top = dynamic_required_hits(symptom_map, top_id)
        hits_top = evidence_hits_by_disease.get(top_id, 0)
        
        if hits_top >= req_hits_top and top_prob >= EARLY_FINALIZE_TOPP:
            finalized = True
            convergence_reason = f"Early finalize: hits {hits_top}/{req_hits_top}, prob {top_prob:.3f}"
            break
        
        if confidence >= SUCCESS_CONFIDENCE and answered_with_lr >= MIN_EVIDENCE_ANSWERS:
            finalized = True
            convergence_reason = f"Confidence threshold: {confidence:.3f} >= {SUCCESS_CONFIDENCE}"
            break
        
        steps += 1
    
    # Final assessment
    sorted_c = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    top_id, top_prob = sorted_c[0]
    confidence, gap = calculate_confidence(candidates, diseases)
    req_hits_top = dynamic_required_hits(symptom_map, top_id)
    hits_top = evidence_hits_by_disease.get(top_id, 0)
    target_prob = candidates.get(target_id, 0.0)
    
    converged = finalized and top_id == target_id
    
    return TestResult(
        disease_id=target_id,
        disease_name=diseases[target_id]["name"],
        test_scenario=scenario_name,
        converged=converged,
        steps=steps,
        final_top_disease=diseases[top_id]["name"],
        final_top_prob=float(top_prob),
        target_prob_at_end=float(target_prob),
        confidence=float(confidence),
        evidence_hits=hits_top,
        required_hits=req_hits_top,
        symptom_path=symptom_sequence,
        posterior_trajectory=posterior_trajectory,
        convergence_reason=convergence_reason if finalized else "Max steps reached",
        errors=errors,
        warnings=warnings
    )


def test_disease_rigorously(
    target_id: int,
    db_path: str = "pediatric.db",
    scenarios_per_disease: int = 10
) -> List[TestResult]:
    """Rigorously test a single disease with multiple scenarios"""
    diseases, priors, symptom_map = load_data(db_path)
    
    # Check if disease has enough evidence
    evidence_count = sum(1 for sym, did_map in symptom_map.items() 
                        if target_id in did_map and did_map[target_id].get("lr_pos"))
    
    if evidence_count < 2:
        return []
    
    generator = MLTestGenerator(diseases, symptom_map, target_id)
    results = []
    
    # Test optimal path
    optimal_path = generator.generate_optimal_path()
    if optimal_path:
        result = simulate_inference(target_id, optimal_path, max_steps=15, db_path=db_path, scenario_name="optimal")
        results.append(result)
    
    # Test suboptimal paths
    for i in range(min(3, scenarios_per_disease - 1)):
        suboptimal_path = generator.generate_suboptimal_path(noise_level=0.3 + i * 0.1)
        result = simulate_inference(target_id, suboptimal_path, max_steps=15, db_path=db_path, scenario_name=f"suboptimal_{i+1}")
        results.append(result)
    
    # Test adversarial path
    adversarial_path = generator.generate_adversarial_path()
    if adversarial_path:
        result = simulate_inference(target_id, adversarial_path, max_steps=15, db_path=db_path, scenario_name="adversarial")
        results.append(result)
    
    # Test random paths
    for i in range(min(3, scenarios_per_disease - len(results))):
        random_path = generator.generate_random_path(length=10)
        result = simulate_inference(target_id, random_path, max_steps=15, db_path=db_path, scenario_name=f"random_{i+1}")
        results.append(result)
    
    # Test diverse paths
    diverse_paths = generator.generate_diverse_paths(n=min(3, scenarios_per_disease - len(results)))
    for i, path in enumerate(diverse_paths):
        if len(results) >= scenarios_per_disease:
            break
        result = simulate_inference(target_id, path, max_steps=15, db_path=db_path, scenario_name=f"diverse_{i+1}")
        results.append(result)
    
    return results


def aggregate_metrics(results: List[TestResult]) -> Dict[int, DiseaseMetrics]:
    """Aggregate metrics by disease"""
    by_disease = defaultdict(list)
    for r in results:
        by_disease[r.disease_id].append(r)
    
    metrics = {}
    for disease_id, disease_results in by_disease.items():
        converged = [r for r in disease_results if r.converged]
        failure_modes = Counter([r.convergence_reason for r in disease_results if not r.converged])
        
        metrics[disease_id] = DiseaseMetrics(
            disease_id=disease_id,
            disease_name=disease_results[0].disease_name,
            total_tests=len(disease_results),
            convergence_rate=len(converged) / len(disease_results) if disease_results else 0.0,
            avg_steps=np.mean([r.steps for r in converged]) if converged else 0.0,
            avg_confidence=np.mean([r.confidence for r in converged]) if converged else 0.0,
            avg_final_prob=np.mean([r.final_top_prob for r in converged]) if converged else 0.0,
            min_steps=min([r.steps for r in converged]) if converged else 0,
            max_steps=max([r.steps for r in converged]) if converged else 0,
            symptom_coverage=0.0,  # Will calculate separately
            evidence_symptom_count=0,  # Will calculate separately
            failure_modes=dict(failure_modes)
        )
    
    return metrics


def generate_report(results: List[TestResult], metrics: Dict[int, DiseaseMetrics], output_file: str):
    """Generate comprehensive test report"""
    diseases, _, _ = load_data("pediatric.db")
    
    report = {
        "test_timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": len(results),
            "total_diseases": len(metrics),
            "total_converged": sum(1 for r in results if r.converged),
            "overall_convergence_rate": sum(1 for r in results if r.converged) / len(results) if results else 0.0,
            "avg_steps": np.mean([r.steps for r in results if r.converged]) if any(r.converged for r in results) else 0.0,
            "avg_confidence": np.mean([r.confidence for r in results if r.converged]) if any(r.converged for r in results) else 0.0,
        },
        "disease_metrics": {did: asdict(m) for did, m in metrics.items()},
        "detailed_results": [asdict(r) for r in results],
        "anomalies": []
    }
    
    # Detect anomalies
    detector = AnomalyDetector()
    if results:
        detector.fit(results)
        for r in results:
            anomalies = detector.detect_anomalies(r)
            if anomalies:
                report["anomalies"].append({
                    "disease": r.disease_name,
                    "scenario": r.test_scenario,
                    "anomalies": anomalies
                })
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report


def main():
    parser = argparse.ArgumentParser(description="Rigorous autotest with ML-based test generation")
    parser.add_argument("--db", type=str, default="pediatric.db", help="Database file path")
    parser.add_argument("--scenarios", type=int, default=10, help="Number of test scenarios per disease")
    parser.add_argument("--max-steps", type=int, default=15, help="Maximum steps per test")
    parser.add_argument("--output", type=str, default="rigorous_test_report.json", help="Output JSON report file")
    parser.add_argument("--only", type=str, default="", help="Comma-separated disease names to test")
    parser.add_argument("--min-evidence", type=int, default=2, help="Minimum evidence symptoms required")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    print("=" * 80)
    print("RIGOROUS AUTOTEST WITH ML-BASED TEST GENERATION")
    print("=" * 80)
    print(f"Database: {args.db}")
    print(f"Scenarios per disease: {args.scenarios}")
    print(f"Max steps: {args.max_steps}")
    print()
    
    diseases, priors, symptom_map = load_data(args.db)
    
    # Select diseases to test
    if args.only:
        name_to_id = {info["name"].lower(): did for did, info in diseases.items()}
        target_ids = [name_to_id.get(n.strip().lower()) for n in args.only.split(",") if n.strip()]
        target_ids = [tid for tid in target_ids if tid is not None]
    else:
        target_ids = list(diseases.keys())
    
    # Filter by evidence count
    filtered_ids = []
    for did in target_ids:
        evidence_count = sum(1 for sym, did_map in symptom_map.items() 
                            if did in did_map and did_map[did].get("lr_pos"))
        if evidence_count >= args.min_evidence:
            filtered_ids.append(did)
    
    print(f"Testing {len(filtered_ids)} diseases...")
    print()
    
    all_results = []
    for i, target_id in enumerate(filtered_ids, 1):
        disease_name = diseases[target_id]["name"]
        if args.verbose:
            print(f"[{i}/{len(filtered_ids)}] Testing {disease_name}...")
        
        results = test_disease_rigorously(target_id, args.db, args.scenarios)
        all_results.extend(results)
        
        if args.verbose:
            converged = sum(1 for r in results if r.converged)
            print(f"  {converged}/{len(results)} scenarios converged")
    
    print()
    print("=" * 80)
    print("GENERATING COMPREHENSIVE REPORT")
    print("=" * 80)
    
    metrics = aggregate_metrics(all_results)
    report = generate_report(all_results, metrics, args.output)
    
    # Print summary
    print(f"\nSUMMARY:")
    print(f"  Total tests: {report['summary']['total_tests']}")
    print(f"  Total diseases: {report['summary']['total_diseases']}")
    print(f"  Converged: {report['summary']['total_converged']}")
    print(f"  Overall convergence rate: {report['summary']['overall_convergence_rate']:.1%}")
    print(f"  Average steps: {report['summary']['avg_steps']:.2f}")
    print(f"  Average confidence: {report['summary']['avg_confidence']:.3f}")
    print(f"  Anomalies detected: {len(report['anomalies'])}")
    
    # Print top failures
    failures = [r for r in all_results if not r.converged]
    if failures:
        print(f"\nFAILURES ({len(failures)}):")
        failure_by_disease = Counter([r.disease_name for r in failures])
        for disease, count in failure_by_disease.most_common(10):
            print(f"  {disease}: {count} failures")
    
    print(f"\nDetailed report saved to: {args.output}")


if __name__ == "__main__":
    main()

