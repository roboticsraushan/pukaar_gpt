import csv
import random

CATEGORIES = [
    ("follow_up", False),
    ("consult", False),
    ("triage", False),
    ("red_flag", True),
    ("non_urgent", False)
]

FOLLOW_UP_TEMPLATES = [
    "We were told to come back for a checkup after {days} days.",
    "The {symptom} has not improved after {days} days of treatment.",
    "My child was given {medication}, but the {symptom} is still there.",
    "We finished the medicine, but my baby is still {symptom_ing}.",
    "The doctor asked us to follow up if the {symptom} did not improve.",
    "My child is still {symptom_ing} after the last visit.",
    "Symptoms have not resolved after {days} days of antibiotics.",
    "We were told to return if {symptom} persisted, and it has.",
]

CONSULT_TEMPLATES = [
    "Should I give {medication} for {symptom}?",
    "Is it safe to give my baby {item} at {age} months?",
    "What should I feed my child with {symptom}?",
    "How can I prevent {complication} in my baby?",
    "When should I take my child to the hospital?",
    "Can I give {medication} to my {age}-month-old?",
    "Is it normal for my baby to {behavior}?",
    "What can I do if my child is {symptom_ing}?",
    "Is it necessary to see a doctor for {symptom}?",
]

TRIAGE_TEMPLATES = [
    "My baby is not feeling well.",
    "I have a health concern about my {age}-year-old.",
    "Can you help me with my child's symptoms?",
    "My child has {symptom} and {symptom2}.",
    "My baby is {symptom_ing} and seems uncomfortable.",
    "My child is {age} months old and has {symptom}.",
    "I am worried about my child's {symptom}.",
    "My baby has been {symptom_ing} for {days} days.",
]

RED_FLAG_TEMPLATES = [
    "My baby is not waking up and is breathing very fast.",
    "My child had a seizure and is not responding.",
    "My child fell and is now unconscious.",
    "My baby is having trouble breathing and making grunting noises.",
    "My baby is not feeding and has blue lips.",
    "My child is vomiting everything and is very weak.",
    "My baby has sunken eyes and no wet diapers for {hours} hours.",
    "My child is not moving and is very floppy.",
    "My baby is extremely lethargic and not responding to touch.",
]

NON_URGENT_TEMPLATES = [
    "My child has a mild cold but is playing normally.",
    "My baby sneezes a lot but has no fever.",
    "My child has a small bruise from falling.",
    "My baby is teething and a bit fussy but otherwise fine.",
    "My child has a runny nose but is eating well.",
    "My baby has a mild rash but is active and alert.",
    "My child has a cough but no breathing problems.",
    "My baby is sleeping well and feeding normally.",
    "My child has a mosquito bite but no swelling or pain.",
]

SYMPTOMS = ["fever", "cough", "diarrhea", "vomiting", "rash", "cold", "breathing difficulty", "constipation", "runny nose", "sneezing", "ear pain", "eye discharge", "stomach pain", "sore throat"]
SYMPTOMS_ING = ["coughing", "vomiting", "sneezing", "crying", "scratching", "refusing to eat", "not sleeping", "not feeding", "not playing", "not moving"]
MEDICATIONS = ["paracetamol", "ibuprofen", "antibiotics", "ORS", "cough syrup"]
ITEMS = ["water", "juice", "honey", "solid food", "milk"]
COMPLICATIONS = ["dehydration", "infection", "fever", "rash", "constipation"]
BEHAVIORS = ["cry a lot", "sleep less", "refuse to eat", "wake up at night", "be fussy"]
AGES = [str(i) for i in range(1, 25)]
DAYS = [str(i) for i in range(1, 15)]
HOURS = [str(i*2) for i in range(1, 13)]

CATEGORY_MAP = {
    "follow_up": (FOLLOW_UP_TEMPLATES, False),
    "consult": (CONSULT_TEMPLATES, False),
    "triage": (TRIAGE_TEMPLATES, False),
    "red_flag": (RED_FLAG_TEMPLATES, True),
    "non_urgent": (NON_URGENT_TEMPLATES, False),
}


def random_case(template, **kwargs):
    return template.format(
        symptom=random.choice(SYMPTOMS),
        symptom2=random.choice(SYMPTOMS),
        symptom_ing=random.choice(SYMPTOMS_ING),
        medication=random.choice(MEDICATIONS),
        item=random.choice(ITEMS),
        complication=random.choice(COMPLICATIONS),
        behavior=random.choice(BEHAVIORS),
        age=random.choice(AGES),
        days=random.choice(DAYS),
        hours=random.choice(HOURS),
    )

def main():
    with open("test_cases.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["description", "message", "expected_flow_type", "expect_urgent"])
        for category, (templates, is_urgent) in CATEGORY_MAP.items():
            for i in range(1000):
                template = random.choice(templates)
                message = random_case(template)
                description = f"{category.capitalize()} case {i+1}"
                expected_flow = category if category != "non_urgent" else "triage"
                writer.writerow([description, message, expected_flow, is_urgent])
    print("Generated test_cases.csv with 5000 cases (1000 per category)")

if __name__ == "__main__":
    main() 