import re

def is_meaningless(text):
    """Detects if a review is gibberish or lacks any substance."""
    text = text.strip()
    
    # 1. Very short reviews (excluding common short positive/negative words)
    common_short_words = {"good", "bad", "nice", "okay", "ok", "cool", "wow", "avg", "meh"}
    if len(text) < 3 and text.lower() not in common_short_words:
        return True, "Your review is too short to be meaningful."

    # 2. Check for keyboard mash (e.g., "asdfghjkl", "qwerty")
    if re.search(r'[asdfghjkl]{5,}|[qwertyuiop]{5,}|[zxcvbnm]{5,}', text.lower()):
        return True, "Please provide a review with actual words."

    # 3. Repeat character strings (e.g., "aaaaaaaaaa", "!!!!!!!!!")
    if re.search(r'(.)\1{4,}', text):
        return True, "Your review contains too many repeated characters."

    # 4. Check vowel ratio (gibberish often lacks vowels or has too many)
    letters = re.sub(r'[^a-zA-Z]', '', text)
    if len(letters) > 4:
        vowels = len(re.findall(r'[aeiouAEIOU]', letters))
        vowel_ratio = vowels / len(letters)
        if vowel_ratio < 0.1 or vowel_ratio > 0.8:
            return True, "The text seems to be gibberish. Please write a proper review."

    # 5. Check for purely numerical or symbolic input
    if not re.search(r'[a-zA-Z]', text):
        return True, "A review must contain at least some letters."

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
    "asdfghjkl",
    "aaaaa",
    "12345",
]

for test in test_cases:
    meaningless, msg = is_meaningless(test)
    print(f"Review: {test}")
    print(f"Meaningless: {meaningless}")
    if meaningless:
        print(f"Message: {msg}")
    print("-" * 20)
