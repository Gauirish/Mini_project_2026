from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
import re

analyzer = SentimentIntensityAnalyzer()

ASPECT_KEYWORDS = {
    "acting": ["acting","performance","actor","actress","cast","portrayal"],
    "story": ["story","plot","screenplay","narrative","storyline"],
    "music": ["music","bgm","soundtrack","score","songs"],
    "direction": ["direction","director","directed","filmmaking"],
    "visuals": ["visuals","cinematography","vfx","effects","shots"],
}


def split_sentences(review):
    # Split by common conjunctions and punctuation to isolate aspects
    # Added more complex conjunctions like "even though", "although"
    pattern = r'but|and|even though|although|while|however|notably|,|\.'
    parts = re.split(pattern, review.lower())
    return [p.strip() for p in parts if p.strip()]


def detect_aspect(sentence):

    for aspect, words in ASPECT_KEYWORDS.items():
        for w in words:
            if w in sentence:
                return aspect

    return None


def sentiment_to_rating(compound):

    rating = (compound + 1) * 2.5
    rating = max(0, min(5, rating))

    return float(round(rating, 1))


def analyze(review):

    sentences = split_sentences(review)

    aspect_scores = {}

    for s in sentences:

        aspect = detect_aspect(s)

        if not aspect:
            continue

        score = analyzer.polarity_scores(s)["compound"]

        rating = sentiment_to_rating(score)

        aspect_scores.setdefault(aspect, []).append(rating)


    aspect_ratings = {}

    for aspect, scores in aspect_scores.items():
        aspect_ratings[aspect] = float(round(np.mean(scores), 1))


    if not aspect_ratings:
        score = analyzer.polarity_scores(review)["compound"]
        overall = sentiment_to_rating(score)
        aspect_ratings["overall"] = float(overall)


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
        "aspects": aspect_ratings
    }