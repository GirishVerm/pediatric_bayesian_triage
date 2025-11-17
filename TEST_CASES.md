# Test Cases for IATRO Convergence Testing

## Test Case 1: Acute Otitis Media

**Patient:** 3-year-old boy

**Presenting Complaint:** Ear pain and fussiness

**Symptoms to Enter (in order):**
1. Ear pain
2. Fever
3. Ear pulling/tugging
4. Irritability

**Expected Diagnosis:** Acute otitis media

**Key Symptoms (High LR+):**
- Ear pulling/tugging (LR+ = 3.50)
- Ear pain (LR+ = 3.40)
- Otorrhea/ear discharge (LR+ = 10.00) - if present
- Fever (LR+ = 1.25)

**Testing Notes:**
- Start with "Ear pain" and "Fever"
- System should suggest "Ear pulling/tugging" as a high-value question
- Should converge to Acute otitis media within 3-5 questions

---

## Test Case 2: Urinary Tract Infection

**Patient:** 5-year-old girl

**Presenting Complaint:** Painful urination and frequent bathroom trips

**Symptoms to Enter (in order):**
1. Dysuria (painful urination)
2. Urinary frequency
3. Urinary urgency
4. Cloudy or bloody urine

**Expected Diagnosis:** Urinary tract infection

**Key Symptoms (High LR+):**
- Back pain or flank pain (LR+ = 5.00) - if present
- Cloudy or bloody urine (LR+ = 4.33)
- Dysuria/painful urination (LR+ = 3.50)
- Urinary urgency (LR+ = 2.60)

**Testing Notes:**
- Start with "Dysuria" and "Urinary frequency"
- System should ask about "Cloudy or bloody urine" and "Back pain"
- Should converge to UTI within 4-6 questions

---

## Test Case 3: Appendicitis

**Patient:** 8-year-old boy

**Presenting Complaint:** Abdominal pain that started around belly button

**Symptoms to Enter (in order):**
1. Abdominal pain
2. Migration of pain from periumbilical to RLQ (right lower quadrant)
3. Right lower quadrant pain
4. McBurney point tenderness
5. Rebound tenderness

**Expected Diagnosis:** Appendicitis

**Key Symptoms (High LR+):**
- Migration of pain from periumbilical to RLQ (LR+ = 7.50) - **Pathognomonic**
- McBurney point tenderness (LR+ = 7.00) - **Pathognomonic**
- Rebound tenderness (LR+ = 4.33)
- Right lower quadrant pain (LR+ = 3.40)

**Testing Notes:**
- Start with "Abdominal pain"
- System should ask about location and migration of pain
- Should converge to Appendicitis within 4-5 questions
- This is a high-severity condition, so system should prioritize it

---

## How to Test

1. **Run IATRO:**
   ```bash
   ./dist/IATRO_original
   # or
   python3 inference_improved.py
   ```

2. **For each test case:**
   - Enter symptoms in the order listed above
   - When system suggests symptoms, select the ones that match the case
   - Continue until system reaches a diagnosis or stops

3. **Record results:**
   - Did it converge to the correct diagnosis? (YES/NO)
   - How many questions did it ask?
   - What was the final confidence/probability?
   - Were the symptom suggestions clinically relevant?

---

## Expected Convergence Behavior

- **Acute otitis media:** Should converge quickly (3-5 questions) with high confidence (>85%)
- **UTI:** Should converge in 4-6 questions with good confidence (>80%)
- **Appendicitis:** Should converge in 4-5 questions with high confidence (>85%) due to pathognomonic findings

---

## Additional Test Scenarios

### Test Case 4: Asthma Exacerbation (Optional)

**Symptoms:**
1. Cough
2. Wheezing
3. Dyspnea (shortness of breath)
4. Chest tightness

**Expected:** Asthma exacerbation

### Test Case 5: Hand-Foot-and-Mouth Disease (Optional)

**Symptoms:**
1. Fever
2. Oral ulcers
3. Vesicular rash on hands
4. Vesicular rash on feet

**Expected:** Hand-foot-and-mouth disease

---

## Tips for Testing

- Enter symptoms in the order they appear in the case
- If system suggests a symptom that matches, select it
- If system suggests something not in the case, select '0' for none
- Don't skip symptoms that are in the case - enter them when suggested
- Note how many questions it takes to converge
- Check if the symptom selection makes clinical sense




