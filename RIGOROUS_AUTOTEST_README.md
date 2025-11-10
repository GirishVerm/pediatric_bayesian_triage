# Rigorous Autotest Script Documentation

## Overview

The `rigorous_autotest.py` script provides **extremely comprehensive testing** of the pediatric diagnosis inference system using machine learning techniques for test case generation, validation, and anomaly detection.

## Key Features

### 1. **ML-Based Test Case Generation**
- **Optimal Path Testing**: Tests with highest LR+ symptoms first (ideal scenario)
- **Suboptimal Path Testing**: Tests with noise and suboptimal symptom selection
- **Adversarial Testing**: Tests with competitor disease symptoms first (worst-case scenario)
- **Random Path Testing**: Tests with random symptom sequences
- **Diverse Path Generation**: Uses clustering to generate diverse test scenarios

### 2. **Comprehensive Metrics**
For each disease, tracks:
- Convergence rate across all scenarios
- Average steps to convergence
- Average confidence at convergence
- Average final probability
- Min/max steps
- Failure modes analysis
- Symptom coverage

### 3. **Anomaly Detection**
- Uses statistical methods to detect unusual convergence patterns
- Identifies:
  - Unusual step counts
  - Low confidence convergences
  - Decreasing posterior probabilities
  - High variance in trajectories

### 4. **Detailed Reporting**
- JSON report with all test results
- Per-disease metrics aggregation
- Anomaly detection results
- Trajectory analysis

## Usage

### Basic Usage
```bash
python3 rigorous_autotest.py
```

### Advanced Options
```bash
python3 rigorous_autotest.py \
    --db pediatric.db \
    --scenarios 10 \
    --max-steps 15 \
    --output rigorous_test_report.json \
    --only "Asthma,Kawasaki Disease" \
    --min-evidence 2 \
    --verbose
```

### Parameters
- `--db`: Database file path (default: `pediatric.db`)
- `--scenarios`: Number of test scenarios per disease (default: 10)
- `--max-steps`: Maximum inference steps per test (default: 15)
- `--output`: Output JSON report file (default: `rigorous_test_report.json`)
- `--only`: Comma-separated disease names to test (default: all diseases)
- `--min-evidence`: Minimum evidence symptoms required (default: 2)
- `--verbose`: Verbose output during testing

## Test Scenarios

### 1. Optimal Path
- Uses symptoms with highest LR+ for target disease
- Tests best-case convergence scenario
- Validates that system can converge when optimal symptoms are presented

### 2. Suboptimal Paths
- Introduces noise (competitor symptoms) at various levels
- Tests robustness to suboptimal symptom selection
- Multiple variants with different noise levels (20-50%)

### 3. Adversarial Path
- Starts with competitor disease symptoms
- Tests worst-case scenario
- Validates system can recover from misleading initial symptoms

### 4. Random Paths
- Random symptom sequences
- Tests general robustness
- Multiple random variants

### 5. Diverse Paths
- Uses ML clustering to generate diverse scenarios
- Ensures comprehensive coverage
- Balances exploration vs exploitation

## Output Report Structure

```json
{
  "test_timestamp": "2025-11-10T...",
  "summary": {
    "total_tests": 1610,
    "total_diseases": 161,
    "total_converged": 1450,
    "overall_convergence_rate": 0.90,
    "avg_steps": 4.2,
    "avg_confidence": 0.95
  },
  "disease_metrics": {
    "4": {
      "disease_id": 4,
      "disease_name": "Asthma exacerbation",
      "total_tests": 10,
      "convergence_rate": 0.90,
      "avg_steps": 3.5,
      "avg_confidence": 0.98,
      ...
    }
  },
  "detailed_results": [...],
  "anomalies": [...]
}
```

## Metrics Explained

### Convergence Rate
Percentage of test scenarios that successfully converged to the target disease.

### Average Steps
Mean number of inference steps required to converge (only for converged tests).

### Average Confidence
Mean confidence score at convergence.

### Failure Modes
Breakdown of why tests failed:
- "Max steps reached"
- "Early finalize: wrong disease"
- "Confidence threshold: wrong disease"

### Anomalies
Detected unusual patterns:
- Unusual step counts (outside 2 standard deviations)
- Low confidence convergences
- Decreasing posterior probabilities
- High variance trajectories

## ML Components

### 1. Test Case Generator (`MLTestGenerator`)
- Analyzes symptom-disease relationships
- Generates diverse test paths using:
  - LR+ analysis
  - Competitor identification
  - Clustering techniques

### 2. Anomaly Detector (`AnomalyDetector`)
- Learns normal ranges from test results
- Uses statistical methods (mean ± 2σ) to detect outliers
- Identifies unusual convergence patterns

### 3. Trajectory Analysis
- Tracks posterior probability over time
- Detects decreasing probabilities
- Identifies high variance patterns

## Comparison with Standard Autotest

| Feature | Standard Autotest | Rigorous Autotest |
|---------|------------------|-------------------|
| Scenarios per disease | 1 | 10+ |
| Test path types | Optimal only | Optimal, suboptimal, adversarial, random, diverse |
| Anomaly detection | No | Yes (ML-based) |
| Trajectory analysis | No | Yes |
| Failure mode analysis | Basic | Comprehensive |
| Report format | Text | JSON with full details |
| ML techniques | No | Yes |

## Example Output

```
================================================================================
RIGOROUS AUTOTEST WITH ML-BASED TEST GENERATION
================================================================================
Database: pediatric.db
Scenarios per disease: 10
Max steps: 15

Testing 161 diseases...

[1/161] Testing Acute otitis media...
  8/10 scenarios converged
[2/161] Testing Asthma exacerbation...
  9/10 scenarios converged
...

SUMMARY:
  Total tests: 1610
  Total diseases: 161
  Converged: 1450
  Overall convergence rate: 90.1%
  Average steps: 4.2
  Average confidence: 0.950
  Anomalies detected: 23

FAILURES (160):
  Concussion: 5 failures
  Crohn's Disease: 3 failures
  ...
```

## Performance Considerations

- **Time**: ~1-2 seconds per test scenario
- **Memory**: Minimal (loads database once)
- **Scalability**: Can test all 161 diseases with 10 scenarios each (~30 minutes)

## Integration with CI/CD

The script can be integrated into CI/CD pipelines:

```bash
# Run tests and check convergence rate
python3 rigorous_autotest.py --scenarios 5 --output test_report.json
CONVERGENCE_RATE=$(python3 -c "import json; r=json.load(open('test_report.json')); print(r['summary']['overall_convergence_rate'])")
if (( $(echo "$CONVERGENCE_RATE < 0.85" | bc -l) )); then
    echo "Convergence rate too low: $CONVERGENCE_RATE"
    exit 1
fi
```

## Future Enhancements

Potential improvements:
1. Reinforcement learning for optimal test path generation
2. Deep learning models for anomaly detection
3. Automated test case optimization
4. Real-time performance monitoring
5. Comparative analysis across database versions

