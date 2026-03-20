from transformers import pipeline
import numpy as np
import re


sentiment_model = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-xlm-roberta-base-sentiment"
)

ASPECT_KEYWORDS = {
    "acting": ["acting","performance","actor","actress","cast","portrayal"],
    "story": ["story","plot","screenplay","narrative","storyline"],
    "music": ["music","bgm","soundtrack","score","songs"],
    "direction": ["direction","director","directed","filmmaking"],
    "visuals": ["visuals","cinematography","vfx","effects","shots"]
}


def split_sentences(review):

    pattern = r'but|and|even though|although|while|however|notably|,|\.'
    parts = re.split(pattern, review.lower())

    return [p.strip() for p in parts if p.strip()]


def detect_aspect(sentence):

    for aspect, words in ASPECT_KEYWORDS.items():
        for w in words:
            if w in sentence:
                return aspect

    return None


def sentiment_to_rating(label, score):

    if label == "positive":
        rating = 3 + (score * 2)

    elif label == "negative":
        rating = 2 - (score * 2)

    else:
        rating = 2.5

    rating = max(0, min(5, rating))

    return float(round(rating,1))

import re

def detect_spam(review):

    spam_score = 0
    text = review.lower()

    # 1 Excessive punctuation
    if review.count("!") > 4:
        spam_score += 1

    # 2 Repeated words (Aggressive spam check)
    words = text.split()
    if len(words) > 5:
        unique_words = set(words)
        if len(unique_words) < len(words) * 0.5:
            spam_score += 1

    # 3 Too many uppercase letters
    if sum(1 for c in review if c.isupper()) > len(review) * 0.5:
        spam_score += 1

    # 4 Promotional words
    promo_words = ["buy now", "watch now", "subscribe", "click here"]

    for p in promo_words:
        if p in text:
            spam_score += 1

    # 5 Repeated characters
    if re.search(r'(.)\1{3,}', text):
        spam_score += 1

    return spam_score >= 2




def is_meaningless(text):
    """Detects if a review is gibberish or lacks any substance."""
    text = text.strip()
    
    # 1. Very short reviews (excluding common short positive/negative words)
    common_short_words = {"good", "bad", "nice", "okay", "ok", "cool", "wow", "avg", "meh", "yes", "no", "hi", "hey"}
    if len(text) < 2:
        return True, "Your review is too short to be meaningful."
    if len(text) < 3 and text.lower() not in common_short_words:
        return True, "Please provide a more descriptive review."

    # 2. Check for keyboard mash (e.g., "asdfghjkl", "qwerty")
    # Increased threshold from 5 to 8 to avoid flagging words like "power", "quiet", "glass"
    if re.search(r'[asdfghjkl]{8,}|[qwertyuiop]{8,}|[zxcvbnm]{8,}', text.lower()):
        return True, "Please provide a review with actual words."

    # 3. Repeat character strings (e.g., "aaaaaaaaaa", "!!!!!!!!!")
    if re.search(r'(.)\1{4,}', text):
        return True, "Your review contains too many repeated characters."

    # 4. Check vowel ratio (gibberish often lacks vowels or has too many)
    # Include 'y' as a vowel and loosen the ratio for words like "rhythm"
    letters = re.sub(r'[^a-zA-Z]', '', text)
    if len(letters) > 4:
        vowels = len(re.findall(r'[aeiouyAEIOUY]', letters))
        vowel_ratio = vowels / len(letters)
        if vowel_ratio < 0.05 or vowel_ratio > 0.9:
            return True, "The text seems to be gibberish. Please write a proper review."

    # 5. Check for purely numerical or symbolic input
    if not re.search(r'[a-zA-Z]', text):
        return True, "A review must contain at least some letters."

    return False, None


def analyze(review):
    # First, check for gibberish/meaningless content
    meaningless, msg = is_meaningless(review)
    if meaningless:
        return {
            "rating": 0,
            "sentiment": "meaningless",
            "aspects": {},
            "is_spam": False,
            "is_meaningless": True,
            "message": f"⚠️ {msg}"
        }

    if detect_spam(review):
        return {
            "rating": 0,
            "sentiment": "spam",
            "aspects": {},
            "is_spam": True,
            "is_meaningless": False,
            "message": "⚠️ This review was flagged as spam and will not affect ratings."
        }
    sentences = split_sentences(review)

    aspect_scores = {}

    for s in sentences:

        aspect = detect_aspect(s)

        if not aspect:
            continue

        result = sentiment_model(s)[0]

        label = result["label"].lower()
        score = result["score"]

        rating = sentiment_to_rating(label, score)

        aspect_scores.setdefault(aspect, []).append(rating)


    aspect_ratings = {}

    for aspect, scores in aspect_scores.items():
        aspect_ratings[aspect] = float(round(np.mean(scores),1))


    if not aspect_ratings:

        result = sentiment_model(review)[0]

        label = result["label"].lower()
        score = result["score"]

        overall = sentiment_to_rating(label, score)

        aspect_ratings["overall"] = overall


    overall_rating = float(round(np.mean(list(aspect_ratings.values())),1))

    if overall_rating >= 4:
        sentiment = "positive"
    elif overall_rating >= 2.5:
        sentiment = "neutral"
    else:
        sentiment = "negative"


    return {
        "rating": overall_rating,
        "sentiment": sentiment,
        "aspects": aspect_ratings,
        "is_spam": False
    }