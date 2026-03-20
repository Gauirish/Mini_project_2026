import re

def is_meaningless(text):
    text = text.strip()
    common_short_words = {"good", "bad", "nice", "okay", "ok", "cool", "wow", "avg", "meh", "yes", "no", "hi", "hey"}
    if len(text) < 2: return True, "too short"
    if len(text) < 3 and text.lower() not in common_short_words: return True, "not descriptive"
    if re.search(r'[asdfghjkl]{8,}|[qwertyuiop]{8,}|[zxcvbnm]{8,}', text.lower()): return True, "keyboard mash"
    if re.search(r'(.)\1{4,}', text): return True, "repeated chars"
    letters = re.sub(r'[^a-zA-Z]', '', text)
    if len(letters) > 4:
        vowels = len(re.findall(r'[aeiouyAEIOUY]', letters))
        ratio = vowels / len(letters)
        if ratio < 0.05 or ratio > 0.9: return True, f"vowel ratio {ratio:.2f}"
    if not re.search(r'[a-zA-Z]', text): return True, "no letters"
    return False, None

test_cases = [
    "This movie was power packed and quiet good.",
    "The glass work in the visuals was amazing.",
    "The route the story took was very quiet.",
    "It falls short of expectations.",
    "I shall watch it again.",
    "The rhythm of the music was great.",
    "Psychology of the characters was deep.",
    "It was a cool movie.",
    "Ok",
    "Yes",
    "asdfghjkl",
    "aaaaa",
    "12345",
]

for test in test_cases:
    meaningless, msg = is_meaningless(test)
    status = "FAIL" if meaningless else "PASS"
    print(f"[{status}] {test} | {msg if meaningless else ''}")
