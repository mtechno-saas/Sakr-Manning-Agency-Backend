import spacy
nlp = spacy.load("en_core_web_sm")

def validate_entity(text, expected_type):
    if not text: return False
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in expected_type:
            return True
    
    # SpaCy often misses capitalized names in CVs, so we add fallbacks
    if expected_type == ["PERSON"] and len(text.split()) >= 2:
        return True
    return False

print("Egyptian is GPE/NORP:", validate_entity("Egyptian", ["GPE", "NORP"]))
print("18/02/1978 is DATE:", validate_entity("18/02/1978", ["DATE"]))
print("MOSAAD HELMY is PERSON:", validate_entity("MOSAAD HELMY", ["PERSON"]))
print("Date of Birth is PERSON:", validate_entity("Date of Birth", ["PERSON"]))
