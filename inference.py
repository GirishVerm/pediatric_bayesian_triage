#!/usr/bin/env python3
import sqlite3
from math import log2
import math
import sys
import os
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
    # New symptoms from latest database additions
    "Pancytopenia": "Low counts of all blood cell types (red cells, white cells, platelets).",
    "Bone marrow failure": "Bone marrow stops making enough blood cells.",
    "Cardiomegaly": "Enlarged heart, seen on imaging.",
    "Arrhythmias": "Irregular or abnormal heart rhythm.",
    "Lymphoblasts on peripheral smear": "Immature white blood cells seen in blood test (indicates leukemia).",
    "Myeloblasts on peripheral smear": "Immature blood cells seen in blood test (indicates leukemia).",
    "Auer rods": "Rod-shaped structures in blood cells (specific to certain leukemias).",
    "Papilledema": "Swelling of the optic nerve at the back of the eye (seen by eye doctor).",
    "Focal neurological signs": "Specific problems like weakness on one side, vision loss, or coordination issues.",
    "Gallop rhythm": "Extra heart sound heard by doctor, like a galloping horse.",
    "Reed-Sternberg cells": "Abnormal cells seen in biopsy (diagnostic of Hodgkin lymphoma).",
    "B symptoms": "Fever, night sweats, or weight loss (associated with lymphomas).",
    "Leukocoria (white pupil)": "White reflection in the pupil instead of red (emergency - see doctor immediately).",
    "Currant jelly stool": "Stool that looks like red jelly mixed with mucus (emergency - see doctor immediately).",
    "Increased head circumference": "Head growing faster than normal for age (measured by doctor).",
    "Bulging fontanelle": "Soft spot on baby's head is raised or bulging (emergency - see doctor immediately).",
    "Sunsetting eyes": "Eyes appear to look downward, showing white above the iris (sign of increased brain pressure).",
    "Inattention": "Difficulty paying attention, easily distracted, forgetful.",
    "Hyperactivity": "Excessive movement, fidgeting, difficulty sitting still.",
    "Impulsivity": "Acting without thinking, interrupting others, difficulty waiting turn.",
    "Social communication deficits": "Difficulty with social interactions, making friends, understanding social cues.",
    "Repetitive behaviors": "Repeating actions, words, or movements over and over.",
    "Restricted interests": "Very focused on specific topics or activities, limited range of interests.",
    "Obsessions": "Repeated, unwanted thoughts that cause anxiety or distress.",
    "Compulsions": "Repetitive behaviors or mental acts that feel necessary to perform.",
    "Time-consuming rituals": "Repetitive behaviors that take a lot of time and interfere with daily life.",
    # Additional symptom explanations for comprehensive coverage
    "22q11.2 deletion": "Genetic test finding (specific chromosome deletion).",
    "ACVRL1 mutation": "Genetic test finding (specific gene mutation).",
    "ADEM-like presentation": "Brain inflammation pattern (seen on imaging).",
    "ASO titer elevation": "Strep antibody test is high (blood test finding).",
    "AVMs": "Abnormal connections between arteries and veins (seen on imaging).",
    "AVNRT pattern": "Specific heart rhythm pattern seen on ECG (heart tracing).",
    "AVRT pattern": "Specific heart rhythm pattern seen on ECG (heart tracing).",
    "Abdominal distension": "Belly is swollen or bloated.",
    "Abdominal mass": "Lump or mass felt in belly (felt by doctor).",
    "Abnormal MRI": "Abnormal findings on brain or spine imaging.",
    "Abnormal echocardiography": "Abnormal findings on heart ultrasound.",
    "Abnormal imaging": "Abnormal findings on any imaging test.",
    "Abnormal skin pigmentation": "Unusual coloring or patches on skin.",
    "Abnormal thyroid function tests": "Thyroid hormone levels are abnormal (blood test finding).",
    "Absence of cough": "No cough present.",
    "Absence of tonsillar exudate": "No white patches on tonsils.",
    "Academic difficulties": "Problems with school performance.",
    "Age 6-24 months": "Child is between 6 and 24 months old.",
    "All pulmonary veins to RA": "Heart defect where lung veins connect to wrong heart chamber (seen on imaging).",
    "Altered mental status": "Confused, drowsy, or not acting normally.",
    "Ambiguous genitalia (females)": "Genitalia appearance is unclear (in newborn girls).",
    "Anemia": "Low red blood cell count (seen on blood test).",
    "Anxiety related to obsessions": "Worry or anxiety connected to repeated thoughts.",
    "Aortic dilation": "Main artery is enlarged (seen on imaging).",
    "Appetite changes": "Eating more or less than usual.",
    "Arachnodactyly": "Long, spider-like fingers.",
    "Arching back after feeds": "Arches back after eating (may indicate discomfort).",
    "Arrhythmia": "Irregular or abnormal heart rhythm.",
    "Ascites": "Fluid buildup in belly (belly looks swollen).",
    "Asian ethnicity": "Of Asian descent (risk factor for some conditions).",
    "Ataxia": "Problems with balance and coordination.",
    "Back pain or flank pain": "Pain in back or side.",
    "Basal collateral vessels": "Abnormal blood vessels at base of brain (seen on imaging).",
    "Bilateral conjunctival injection without exudate": "Both eyes are red but no discharge.",
    "Bilateral involvement": "Both sides of body affected.",
    "Bilateral optic neuritis": "Both eyes affected by optic nerve inflammation.",
    "Birbeck granules": "Specific structures seen under microscope (diagnostic finding).",
    "Bleeding": "Bleeding that is excessive or unusual.",
    "Blood pressure gradient": "Different blood pressure in arms vs. legs (measured by doctor).",
    "Bloody diarrhea": "Loose stools with blood in them.",
    "Bloody stools": "Stool has blood in it.",
    "Bone lesions": "Abnormal areas in bones (seen on imaging).",
    "Bone marrow findings": "Abnormal findings in bone marrow (seen on bone marrow test).",
    "Bone pain": "Pain in bones.",
    "Both great arteries from RV": "Heart defect where both main arteries come from right ventricle (seen on imaging).",
    "Bounding pulses": "Strong, forceful pulse that can be felt easily.",
    "Bowel/bladder dysfunction": "Problems controlling bowel or bladder.",
    "Bruising or petechiae": "Bruises or tiny red spots on skin (sign of bleeding problem).",
    "CD1a positive cells": "Specific cell type seen on biopsy (diagnostic finding).",
    "CD207 positive": "Specific marker on cells (diagnostic finding).",
    "Café-au-lait spots": "Light brown spots on skin (like coffee with milk).",
    "Cervical lymphadenopathy (>1.5 cm)": "Swollen glands in neck larger than 1.5 cm (felt by doctor).",
    "Characteristic angiography": "Specific pattern on blood vessel imaging.",
    "Chest pain": "Pain or discomfort in the chest area.",
    "Child appears well despite high fever": "Child looks and acts well even with high fever.",
    "Chronic cough": "Cough lasting longer than 4 weeks.",
    "Chronic diarrhea": "Loose stools lasting longer than 2 weeks.",
    "Cloudy or bloody urine": "Urine looks cloudy or has blood in it.",
    "Clubbing": "Fingertips and toes become rounded and enlarged (sign of chronic low oxygen).",
    "Coagulopathy": "Problems with blood clotting (seen on blood test).",
    "Coarctation of aorta": "Narrowing of main artery (seen on imaging).",
    "Cognitive changes": "Changes in thinking, memory, or understanding.",
    "Collateral vessels": "Extra blood vessels that develop (seen on imaging).",
    "Comedones (blackheads/whiteheads)": "Blackheads or whiteheads on skin.",
    "Compression on imaging": "Something pressing on structures (seen on imaging).",
    "Conal septum malalignment": "Heart wall structure misaligned (seen on imaging).",
    "Congenital anomalies": "Birth defects or abnormalities present from birth.",
    "Constipation": "Hard, dry stools that are difficult to pass.",
    "Consumptive coagulopathy": "Blood clotting system being used up (seen on blood test).",
    "Consumptive coagulopathy pattern": "Specific pattern of blood clotting problems (seen on blood test).",
    "Continuous machinery murmur": "Specific heart sound that sounds like machinery (heard by doctor).",
    "Cough (especially at night)": "Cough that is worse at night.",
    "Cough present": "Has a cough.",
    "Cyanosis": "Blue or purple coloring of skin, lips, or nails (sign of low oxygen).",
    "Cyanosis at birth": "Blue coloring present from birth (sign of low oxygen).",
    "DKC1 mutation": "Genetic test finding (specific gene mutation).",
    "Decreased urine output": "Making less urine than usual.",
    "Dehydration": "Not enough water in body (dry mouth, sunken eyes, few tears).",
    "Delayed passage of meconium": "First stool after birth is delayed (in newborns).",
    "Delayed speech": "Speech development is delayed for age.",
    "Developmental delay": "Not reaching developmental milestones on time (sitting, walking, talking).",
    "DiGeorge syndrome": "Genetic syndrome with multiple problems.",
    "Diabetes insipidus": "Condition causing excessive thirst and urination.",
    "Differential cyanosis": "Blue coloring in some areas but not others (sign of heart problem).",
    "Dizziness": "Feeling lightheaded or like room is spinning.",
    "Double-chambered right ventricle": "Right heart chamber has extra wall (seen on imaging).",
    "Double-inlet connection": "Heart defect where both upper chambers connect to one lower chamber (seen on imaging).",
    "Dysphagia": "Difficulty swallowing.",
    "Dyspnea": "Shortness of breath or difficulty breathing.",
    "Dysuria": "Pain or burning when peeing.",
    "ECG abnormalities": "Abnormal findings on heart tracing test.",
    "ECG changes": "Changes seen on heart tracing test.",
    "ECG findings": "Findings from heart tracing test.",
    "ENG mutation": "Genetic test finding (specific gene mutation).",
    "ESR/CRP elevation": "Inflammation markers are high (blood test finding).",
    "Easy bruising": "Bruises easily or has many bruises.",
    "Edema": "Swelling, usually in legs, feet, or around eyes.",
    "Elevated amylase/lipase": "Pancreas enzyme tests are high (blood test finding).",
    "Elevated creatinine": "Kidney function test is high (blood test finding).",
    "Elevated liver enzymes": "Liver function tests are high (blood test finding).",
    "Elevated pulmonary artery pressure": "High pressure in lung arteries (seen on imaging or test).",
    "Elevated troponin": "Heart muscle damage test is high (blood test finding).",
    "Embolic phenomena": "Blood clots traveling to other parts of body.",
    "Enterocolitis": "Severe inflammation of intestines (emergency).",
    "Epigastric pain radiating to back": "Pain in upper belly that spreads to back.",
    "Epistaxis": "Nosebleeds.",
    "Epistaxis frequency": "Frequent nosebleeds.",
    "Evidence of group A strep infection": "Signs of strep infection (test or symptoms).",
    "Excessive bleeding": "Bleeding that is heavy or won't stop.",
    "Excessive worry": "Worries too much about many things.",
    "Exercise intolerance": "Gets tired easily with physical activity.",
    "Extraintestinal manifestations": "Problems in other parts of body (joints, skin, eyes).",
    "Eye redness (bilateral)": "Both eyes are red.",
    "Facial angiofibromas": "Small red bumps on face (specific skin finding).",
    "Facial bone changes": "Changes in facial bone structure (seen on imaging).",
    "Facial pain/pressure": "Pain or pressure in face, especially around nose/cheeks.",
    "Failure to thrive": "Not growing or gaining weight as expected.",
    "Family history": "Condition runs in the family.",
    "Family history of bleeding": "Family members have bleeding problems.",
    "Fatigue": "Extreme tiredness or lack of energy.",
    "Feeding intolerance": "Cannot tolerate feeding, may vomit or have problems.",
    "Feeling of incomplete evacuation": "Feels like bowel movement is not finished.",
    "Fever ≥5 days": "Fever lasting 5 days or longer.",
    "Frequency or urgency": "Needing to pee very often or urgently.",
    "Fussiness after feeds": "Fussy or irritable after eating.",
    "GI bleeding": "Bleeding from digestive tract (may see blood in vomit or stool).",
    "Goiter": "Enlarged thyroid gland (swelling in neck).",
    "Gradual onset": "Symptoms started slowly.",
    "Hard or lumpy stools": "Stools are hard or have lumps.",
    "Head injury": "Injury to the head (may be emergency).",
    "Heart failure": "Heart not pumping blood effectively.",
    "Heart murmur": "Extra sound heard when doctor listens to heart.",
    "Heat/cold intolerance": "Very sensitive to hot or cold temperatures.",
    "Hepatic encephalopathy": "Brain problems due to liver failure (confusion, drowsiness).",
    "Hepatomegaly": "Enlarged liver (felt by doctor).",
    "High fever lasting 3-5 days": "High temperature lasting 3 to 5 days.",
    "Histiocytes on biopsy": "Specific cell type seen on tissue sample (diagnostic finding).",
    "History of asthma": "Has asthma.",
    "History of rheumatic fever": "Had rheumatic fever in the past.",
    "Hydrocephalus": "Too much fluid in brain (seen on imaging).",
    "Hyperammonemia": "High ammonia level in blood (seen on blood test).",
    "Hypercyanotic spells": "Episodes of severe blue coloring and difficulty breathing (emergency).",
    "Hyperpigmentation": "Dark patches on skin (in certain conditions).",
    "Hypertension": "High blood pressure (measured by doctor).",
    "Hypomelanotic macules": "Light-colored patches on skin (like white spots).",
    "Hypotonia": "Low muscle tone, feels floppy.",
    "INR > 1.5": "Blood clotting test shows increased bleeding risk (blood test finding).",
    "Increased adenosine deaminase": "High level of specific enzyme (seen on blood test).",
    "Increased fetal hemoglobin": "High level of fetal hemoglobin (seen on blood test).",
    "Increased head circumference": "Head growing faster than normal for age (measured by doctor).",
    "Infantile hemangioma": "Red birthmark that grows (vascular tumor).",
    "Infections": "Frequent or severe infections.",
    "Inflammatory papules and pustules": "Red bumps and pus-filled bumps on skin.",
    "Infrequent bowel movements (<3 per week)": "Fewer than 3 bowel movements per week.",
    "Irregular pulse": "Heartbeat is not regular (felt by doctor).",
    "Irritability": "Easily annoyed or upset.",
    "Irritability in infants": "Baby is fussy or easily upset.",
    "Isolated thrombocytopenia": "Only platelets are low, other blood cells normal (seen on blood test).",
    "Itchy or watery eyes": "Eyes that are itchy or tear up.",
    "Jaundice": "Yellow coloring of skin and eyes (sign of liver problem).",
    "Joint bleeding": "Bleeding into joints causing pain and swelling.",
    "Joint pain/swelling": "Painful or swollen joints.",
    "Jones criteria": "Specific set of criteria for diagnosing rheumatic fever.",
    "Lacy reticular rash on body": "Lacy, net-like rash on the body.",
    "Learning difficulties": "Problems with learning or schoolwork.",
    "Lens dislocation": "Lens of eye is out of place (seen by eye doctor).",
    "Lethargy": "Extreme tiredness, hard to wake up, or very low energy.",
    "Leukoplakia": "White patches in mouth that don't scrape off.",
    "Lisch nodules": "Small bumps on iris of eye (seen by eye doctor).",
    "Longitudinally extensive myelitis": "Spinal cord inflammation pattern (seen on imaging).",
    "Loss of consciousness": "Passing out or fainting.",
    "Loss of interest": "Loses interest in things they used to enjoy.",
    "Low neutrophil count": "Low count of infection-fighting white blood cells (seen on blood test).",
    "Low platelet count": "Not enough platelets for blood clotting (seen on blood test).",
    "Low reticulocyte count": "Low count of young red blood cells (seen on blood test).",
    "Lower extremity weakness": "Weakness in legs.",
    "Lymphadenopathy": "Swollen lymph nodes or glands.",
    "MOG antibodies positive": "Specific antibody test positive (blood test finding).",
    "Macrocytic anemia": "Large red blood cells with low count (seen on blood test).",
    "Maculopapular rash appearing after fever resolves": "Flat and bumpy rash appearing after fever goes away.",
    "Malposition of great arteries": "Main heart arteries in wrong position (seen on imaging).",
    "Maxillary tooth pain": "Pain in upper teeth.",
    "McBurney point tenderness": "Pain when pressing specific spot in lower right belly (diagnostic sign).",
    "Menorrhagia (females)": "Very heavy or prolonged menstrual periods (in adolescent girls).",
    "Microcytic red cells": "Small red blood cells (seen on blood test).",
    "Migration of pain from periumbilical to RLQ": "Pain moved from belly button area to lower right.",
    "Mild symptoms": "Symptoms are not severe.",
    "Mitral regurgitation": "Heart valve leaking backward (seen on imaging).",
    "Mitral stenosis": "Heart valve narrowed (seen on imaging).",
    "Morning headache": "Headache that is worse in the morning.",
    "Mouth ulcers": "Sores or ulcers in the mouth.",
    "Moyamoya vessels": "Specific pattern of blood vessels in brain (seen on imaging).",
    "Mucus in stool": "Mucus (slimy substance) in the stool.",
    "Muscle wasting": "Muscles are getting smaller.",
    "Nail dystrophy": "Abnormal or deformed nails.",
    "Narrow QRS complex": "Specific pattern on heart tracing test.",
    "Nausea and vomiting": "Feeling sick to stomach and throwing up.",
    "Nausea or vomiting": "Feeling sick to stomach or throwing up.",
    "Neurological deficits": "Problems with brain or nervous system function.",
    "Neurofibromas": "Soft bumps on or under skin (tumors of nerve tissue).",
    "Neutropenia": "Low count of infection-fighting white blood cells (seen on blood test).",
    "Night sweats": "Excessive sweating at night, soaking through clothes.",
    "No fever or low-grade fever": "No fever or only mild fever.",
    "Notching of ribs": "Ribs have notches (seen on chest X-ray).",
    "Obstructed TAPVR": "Blocked blood flow from lungs (seen on imaging).",
    "Open neural tube defect": "Birth defect where spine or brain doesn't close properly (seen at birth).",
    "Optic neuritis": "Inflammation of optic nerve causing vision problems.",
    "Oral discomfort": "Discomfort in mouth.",
    "Pallor": "Pale skin color.",
    "Palpitations": "Feeling of heart racing, fluttering, or skipping beats.",
    "Paroxysmal episodes": "Sudden episodes that come and go.",
    "Perianal abscess": "Infected area around anus (may need drainage).",
    "Perianal disease": "Problems around the anus.",
    "Perianal fistula": "Abnormal tunnel from anus to skin (seen by doctor).",
    "Perianal pruritus": "Itching around anus.",
    "Pericardial friction rub": "Specific sound heard when doctor listens to heart (like rubbing).",
    "Periorbital ecchymosis": "Bruising around eyes.",
    "Peripheral edema": "Swelling in legs or feet.",
    "Persistent sadness": "Sad or down mood that lasts.",
    "Petechiae": "Tiny red spots on skin that don't fade when pressed (sign of bleeding problem).",
    "Physical symptoms (headache, stomachache)": "Physical complaints like headache or stomachache.",
    "Platelet trapping": "Platelets being used up abnormally (seen on blood test).",
    "Pneumatosis intestinalis": "Gas bubbles in intestinal wall (seen on imaging, may be emergency).",
    "Polycythemia": "Too many red blood cells (seen on blood test).",
    "Polydipsia": "Excessive thirst, drinking a lot.",
    "Polymorphous rash": "Rash that has different types of spots.",
    "Polyuria": "Excessive urination, peeing a lot.",
    "Poor vision": "Trouble seeing.",
    "Poor weight gain": "Not gaining weight as expected for age.",
    "Positional chest pain": "Chest pain that changes with position.",
    "Positive blood cultures": "Bacteria found in blood (blood test finding).",
    "Positive sweat test": "Sweat test is positive (diagnostic test for cystic fibrosis).",
    "Positive ultrasound": "Abnormal findings on ultrasound imaging.",
    "Postductal coarctation": "Narrowing of main artery after birth (seen on imaging).",
    "Progressive muscle weakness": "Muscle weakness that gets worse over time.",
    "Prolonged bleeding": "Bleeding that takes longer than normal to stop.",
    "Prolonged bleeding after injury": "Bleeding continues too long after injury.",
    "Pruritus": "Itching.",
    "Pruritus of scalp": "Itchy scalp.",
    "Pulmonary fibrosis": "Scarring in lungs (seen on imaging).",
    "Purpura": "Purple spots or patches on skin (sign of bleeding problem).",
    "Purulent rhinorrhea with unilateral predominance": "Thick yellow/green mucus from one side of nose.",
    "RPS19 mutation": "Genetic test finding (specific gene mutation).",
    "Raised welts or wheals": "Raised, itchy bumps on skin that come and go (hives).",
    "Rapid heart rate": "Heart beating faster than normal for age.",
    "Rash appears exactly as fever breaks": "Rash appears right when fever goes away.",
    "Rash improves with cooling": "Rash gets better when child cools down.",
    "Rash in areas of sweating": "Rash where child sweats most.",
    "Rash in different stages": "Rash has different types of spots at same time.",
    "Rash in skin folds": "Rash in areas where skin folds (armpits, groin, etc.).",
    "Rebound tenderness": "Pain when releasing pressure on belly (diagnostic sign).",
    "Recent viral illness": "Had a virus recently.",
    "Rectal involvement": "Rectum is affected (seen on exam or imaging).",
    "Recurrent infections": "Frequent infections.",
    "Recurrent pulmonary infections": "Frequent lung infections.",
    "Recurrent respiratory infections": "Frequent lung or breathing infections.",
    "Red eye": "Red or pink eye.",
    "Refusing feeds": "Refuses to eat or drink.",
    "Regurgitation": "Spitting up or bringing food back up.",
    "Respiratory difficulties": "Trouble breathing.",
    "Respiratory distress": "Working hard to breathe, may see ribs pulling in.",
    "Response to adenosine": "Heart rhythm responds to specific medication (test finding).",
    "Restlessness": "Can't sit still, fidgety.",
    "Rhinorrhea (runny nose) present": "Has a runny nose.",
    "Right lower quadrant pain": "Pain in lower right belly.",
    "Right subclavian artery anomaly": "Abnormal artery pattern (seen on imaging).",
    "Right upper quadrant pain": "Pain in upper right belly.",
    "Right ventricular hypertrophy": "Right heart chamber is enlarged (seen on imaging).",
    "Right-to-left shunt": "Blood bypasses lungs (heart defect, seen on imaging).",
    "Ring-shaped rash": "Rash that forms a ring shape.",
    "Roth spots": "Small red spots in retina (seen by eye doctor).",
    "Salt-wasting crisis": "Severe salt loss causing dehydration (emergency).",
    "Sandifer syndrome": "Specific pattern of arching back and head turning (associated with reflux).",
    "Scaling at border": "Flaky skin at edge of rash.",
    "Seasonal pattern": "Symptoms happen at certain times of year.",
    "Seizure": "Sudden episode of shaking or unusual behavior (may be emergency).",
    "Seizures": "Repeated episodes of shaking or unusual behavior.",
    "Sensory deficits": "Problems with feeling or sensation.",
    "Sensory sensitivities": "Very sensitive to sounds, lights, textures, etc.",
    "Serum MOG-IgG positive": "Specific antibody test positive (blood test finding).",
    "Short telomeres": "Telomeres are shorter than normal (genetic test finding).",
    "Shortness of breath": "Hard to catch breath.",
    "Single arterial trunk": "Heart defect with single main artery instead of two (seen on imaging).",
    "Single ventricle": "Heart defect with only one lower pumping chamber (seen on imaging).",
    "Skin rash": "Any rash on the skin.",
    "Skull lesions": "Abnormal areas in skull bones (seen on imaging).",
    "Slapped-cheek facial rash (pathognomonic)": "Bright red cheeks, like a slap mark (very specific finding).",
    "Sleep changes": "Sleeping more or less than usual.",
    "Sleep disturbances": "Problems with sleep.",
    "Small left atrium": "Left upper heart chamber is small (seen on imaging).",
    "Small red bumps": "Small red raised spots on skin.",
    "Social difficulties": "Problems with social interactions.",
    "Spherocytes on peripheral smear": "Round red blood cells (seen on blood test).",
    "Spitting up after feeds": "Spits up after eating.",
    "Splenomegaly": "Enlarged spleen (felt by doctor).",
    "Stenosis of ICA terminus": "Narrowing of main brain artery (seen on imaging).",
    "Strabismus": "Eyes don't align properly (crossed eyes or wandering eye).",
    "Straining during bowel movements": "Having to push hard to have a bowel movement.",
    "Strawberry tongue": "Tongue looks red and bumpy like a strawberry.",
    "Stroke": "Sudden loss of brain function (emergency).",
    "Subaortic VSD": "Hole in heart wall below main artery (seen on imaging).",
    "Subaortic stenosis": "Narrowing below main heart artery (seen on imaging).",
    "Sudden focal neurological deficit": "Sudden weakness, numbness, or problems on one side of body (emergency).",
    "Supracardiac drainage": "Blood vessels drain to wrong location (seen on imaging).",
    "Switched great arteries": "Main heart arteries are switched (seen on imaging).",
    "Symptoms last 7-10 days": "Symptoms continue for 7 to 10 days.",
    "Syncope": "Fainting or passing out.",
    "Tachypnea": "Breathing faster than normal for age.",
    "Tall stature": "Unusually tall for age.",
    "Telangiectasias": "Small visible blood vessels on skin (like tiny red lines).",
    "Telomere length testing": "Genetic test measuring telomere length (blood test).",
    "Tenderness on palpation": "Pain when doctor presses on area.",
    "Tenesmus": "Feeling of needing to have bowel movement even when empty.",
    "Tet spells": "Episodes of severe blue coloring and difficulty breathing in heart defects (emergency).",
    "Thrombocytopenia": "Low platelet count (seen on blood test).",
    "Thumb anomalies": "Thumb is abnormal or missing.",
    "Tonsillar exudate": "White patches or pus on the tonsils.",
    "Transient ischemic attacks": "Brief episodes of stroke-like symptoms that resolve.",
    "Transposition of great arteries": "Main heart arteries are switched (seen on imaging).",
    "Transverse myelitis": "Inflammation of spinal cord causing weakness or numbness.",
    "Truncal valve abnormalities": "Heart valve problems (seen on imaging).",
    "Type B interruption": "Specific type of heart artery defect (seen on imaging).",
    "Type I truncus": "Specific type of heart defect (seen on imaging).",
    "Upper extremity hypertension": "High blood pressure in arms (measured by doctor).",
    "Urgency": "Strong sudden need to pee.",
    "Valvular heart disease": "Problems with heart valves (seen on imaging).",
    "Vascular tumor": "Tumor made of blood vessels (seen on imaging).",
    "Vaso-occlusive crisis": "Severe pain episodes (in sickle cell disease).",
    "Verrucous papules": "Wart-like bumps on skin.",
    "Vertical vein": "Abnormal blood vessel pattern (seen on imaging).",
    "Visible nits on hair shafts": "Can see lice eggs attached to hair.",
    "Visible worms in perianal area": "Can see small white worms around anus (usually at night).",
    "Watery discharge": "Clear, watery fluid coming from nose or eyes.",
    "Weak/absent femoral pulses": "Weak or missing pulse in groin area.",
    "Weak/absent pulses": "Weak or missing pulses in arms/legs.",
    "Weakness on one side": "Weakness affecting one side of body.",
    "Weight changes": "Weight going up or down unexpectedly.",
    "Weight loss": "Losing weight unintentionally.",
    "Welts change location": "Raised bumps move to different areas of skin (hives).",
    "White plaques on oral mucosa": "White patches in mouth that can be scraped off.",
    "Wide pulse pressure": "Large difference between top and bottom blood pressure numbers.",
    "Worsening after initial improvement": "Got better then got worse again.",
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
    parser.add_argument("--db", type=str, default="pediatric.db", help="Database file path")
    args = parser.parse_args()

    try:
        diseases, priors, symptom_map = load_data(args.db)
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
