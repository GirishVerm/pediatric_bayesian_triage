# Quick Start Guide for Medical Students

## Running IATRO

### Option 1: Using the Executable (Easiest)

1. **Download the IATRO executable**
   - macOS: `IATRO.dmg` - Double-click to mount, then drag IATRO to Applications
   - Windows: `IATRO.exe` - Double-click to run
   - Linux: `IATRO` - Make executable (`chmod +x IATRO`) then run (`./IATRO`)

2. **Run the program**
   - Double-click the executable (or run from terminal)
   - The program will start in a terminal/console window

3. **Use the program**
   - Follow the prompts to enter symptoms
   - Select symptoms that match your case
   - The system will suggest a diagnosis

### Option 2: Using Python (If you have Python installed)

1. **Install Python 3.10+** (if not already installed)
   - Download from: https://www.python.org/downloads/

2. **Run the program**
   ```bash
   python inference_improved.py
   ```

3. **Use the program**
   - Follow the prompts to enter symptoms
   - Select symptoms that match your case
   - The system will suggest a diagnosis

## Testing Your Cases

1. **Select a case** from your pediatric textbook or homework
2. **Note the actual diagnosis** from the textbook/case answer
3. **Run IATRO** and enter symptoms as they appear in the case
4. **Record the results** using the testing form provided

## Example Usage

```
Pediatric Disease Diagnosis System (Improved)
==================================================
Select symptoms the child HAS. No need to confirm negatives.

Current top diagnoses:
Acute otitis media (P=0.234)
Bronchiolitis (P=0.189)
Community-acquired pneumonia (P=0.156)

Next symptom options (choose one that IS present):
1. Ear pain
   What it means: Pain in or around the ear; child may be fussy or cry.
   Positive LR coverage: 8 diseases

2. Fever
   What it means: Temperature 38°C (100.4°F) or higher.
   Positive LR coverage: 15 diseases

Choose symptom 1-15 that the child HAS (or '0' for none, 's' to skip, 'q' to quit): 1
```

## Tips

- Enter symptoms in the order they appear in your case
- If a suggested symptom matches your case, select it
- If none match, enter '0' for none or 's' to skip
- Enter 'q' to quit at any time
- The system explains medical terms in plain language

## Troubleshooting

**"Database not found" error:**
- Make sure `pediatric.db` is in the same directory as the executable
- If using Python, ensure you're in the project directory

**Program won't start:**
- macOS: Right-click and select "Open" (may need to allow in Security settings)
- Windows: Check if antivirus is blocking it (may be a false positive)

**Questions?**
Contact: [your contact email]




