from transformers import pipeline
import numpy as np
import re


sentiment_model = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment"
)

ASPECT_KEYWORDS = {
    "acting": ["acting", "performance", "actor", "actress", "cast", "portrayal"],
    "story": ["story", "plot", "screenplay", "narrative", "storyline"],
    "music": ["music", "bgm", "soundtrack", "score", "songs"],
    "direction": ["direction", "director", "directed", "filmmaking"],
    "visuals": ["visuals", "cinematography", "vfx", "effects", "shots"]
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
    """
    nlptown model returns labels like '1 star', '2 stars', ..., '5 stars'.
    We map these directly to a 0-5 scale with a slight score-based nudge.
    """
    stars = int(label.split()[0])  # extract the number from "3 stars"
    # Nudge slightly within the star bucket based on confidence
    # e.g. a very confident 4-star is closer to 4.5, a weak one closer to 3.5
    nudge = (score - 0.5) * 0.8  # ranges roughly from -0.4 to +0.4
    rating = stars + nudge
    rating = max(0.0, min(5.0, rating))
    return float(round(rating, 1))


def analyze_long_text(text):
    """
    Splits long reviews into word-based chunks (~80 words each, ~400 tokens)
    to avoid truncation. Returns averaged label + score.
    """
    words = text.split()
    chunk_size = 80
    chunks = [
        " ".join(words[i:i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]

    results = [sentiment_model(chunk)[0] for chunk in chunks]

    # Average star ratings across chunks
    star_scores = [int(r["label"].split()[0]) for r in results]
    confidence_scores = [r["score"] for r in results]

    avg_stars = np.mean(star_scores)
    avg_confidence = np.mean(confidence_scores)

    # Reconstruct a synthetic label from the average
    rounded = int(round(avg_stars))
    rounded = max(1, min(5, rounded))
    synthetic_label = f"{rounded} star{'s' if rounded > 1 else ''}"

    return {"label": synthetic_label, "score": float(avg_confidence)}


def detect_spam(review):
    spam_score = 0
    text = review.lower()

    if review.count("!") > 4:
        spam_score += 1

    words = text.split()
    if len(words) > 5:
        unique_words = set(words)
        if len(unique_words) < len(words) * 0.5:
            spam_score += 1

    if sum(1 for c in review if c.isupper()) > len(review) * 0.5:
        spam_score += 1

    promo_words = ["buy now", "watch now", "subscribe", "click here"]
    for p in promo_words:
        if p in text:
            spam_score += 1

    if re.search(r'(.)\1{3,}', text):
        spam_score += 1

    return spam_score >= 2


def is_meaningless(text):
    """Detects if a review is gibberish or lacks any substance."""
    text = text.strip()

    common_short_words = {"good", "bad", "nice", "okay", "ok", "cool", "wow", "avg", "meh", "yes", "no", "hi", "hey"}
    if len(text) < 2:
        return True, "Your review is too short to be meaningful."
    if len(text) < 3 and text.lower() not in common_short_words:
        return True, "Please provide a more descriptive review."

    if re.search(r'[asdfghjkl]{8,}|[qwertyuiop]{8,}|[zxcvbnm]{8,}', text.lower()):
        return True, "Please provide a review with actual words."

    if re.search(r'(.)\1{4,}', text):
        return True, "Your review contains too many repeated characters."

    letters = re.sub(r'[^a-zA-Z]', '', text)
    if len(letters) > 4:
        vowels = len(re.findall(r'[aeiouyAEIOUY]', letters))
        vowel_ratio = vowels / len(letters)
        if vowel_ratio < 0.05 or vowel_ratio > 0.9:
            return True, "The text seems to be gibberish. Please write a proper review."

    if not re.search(r'[a-zA-Z]', text):
        return True, "A review must contain at least some letters."

    return False, None


def analyze(review):
    # Check for gibberish/meaningless content
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

        # Use chunked analysis per sentence (handles long sentences too)
        result = analyze_long_text(s)
        label = result["label"]
        score = result["score"]
        rating = sentiment_to_rating(label, score)
        aspect_scores.setdefault(aspect, []).append(rating)

    aspect_ratings = {}
    for aspect, scores in aspect_scores.items():
        aspect_ratings[aspect] = float(round(np.mean(scores), 1))

    # Fallback: no aspects detected — analyze full review
    if not aspect_ratings:
        result = analyze_long_text(review)
        label = result["label"]
        score = result["score"]
        overall = sentiment_to_rating(label, score)
        aspect_ratings["overall"] = overall

    overall_rating = float(round(np.mean(list(aspect_ratings.values())), 1))

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
        "is_spam": False,
        "is_meaningless": False
    }