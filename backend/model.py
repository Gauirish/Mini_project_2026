from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
from deep_translator import GoogleTranslator
from langdetect import detect

# Load once when server starts
model_name = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
tokenizer  = AutoTokenizer.from_pretrained(model_name)
model      = AutoModelForSequenceClassification.from_pretrained(model_name)


def predict(review: str) -> dict:
    inputs = tokenizer(review, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)

    probs = F.softmax(outputs.logits, dim=-1)
    predicted_class = torch.argmax(probs).item()

    return {
        "label": model.config.id2label[predicted_class],
        "confidence": round(probs[0][predicted_class].item(), 3),
        "scores": {
            "negative": probs[0][0].item(),
            "neutral": probs[0][1].item(),
            "positive": probs[0][2].item(),
        }
    }


def score_to_rating(scores: dict) -> float:
    return round(
        (scores["positive"] * 5.0)
        + (scores["neutral"] * 3.0)
        + (scores["negative"] * 1.0),
        1
    )


ASPECT_KEYWORDS = {
    "acting": {
        "positive": ["acting", "performance", "portrayed", "actor", "actress", "brilliant", "convincing", "nailed"],
        "negative": ["overacting", "wooden", "stiff", "unconvincing", "bad acting"]
    },
    "story": {
        "positive": ["story", "plot", "screenplay", "narrative", "gripping", "engaging", "twist"],
        "negative": ["boring plot", "weak story", "predictable", "no plot", "makes no sense"]
    },
    "bgm": {
        "positive": ["music", "bgm", "soundtrack", "score", "background music", "melodious"],
        "negative": ["terrible music", "bad bgm", "annoying music"]
    },
    "direction": {
        "positive": ["direction", "directed", "director", "pacing", "well made", "crafted"],
        "negative": ["mishandled", "poor direction", "poorly directed"]
    },
    "visuals": {
        "positive": ["cinematography", "visuals", "beautiful shots", "vfx", "stunning", "gorgeous"],
        "negative": ["bad vfx", "poor visuals", "cheap looking"]
    }
}


def extract_aspects(review: str, base_rating: float) -> dict:
    review_lower = review.lower()
    aspects = {}

    for aspect, keywords in ASPECT_KEYWORDS.items():
        pos_hits = sum(1 for kw in keywords["positive"] if kw in review_lower)
        neg_hits = sum(1 for kw in keywords["negative"] if kw in review_lower)

        if pos_hits == 0 and neg_hits == 0:
            aspects[aspect] = None
        else:
            boost = (pos_hits - neg_hits) * 0.3
            aspects[aspect] = round(
                min(5.0, max(1.0, base_rating + boost)),
                1
            )

    return aspects


def translate_to_english(review: str) -> str:
    try:
        if detect(review) == "en":
            return review
        return GoogleTranslator(source="auto", target="en").translate(review)
    except:
        return review


def analyze(review: str) -> dict:
    english_review = translate_to_english(review)

    result = predict(english_review)
    rating = score_to_rating(result["scores"])
    aspects = extract_aspects(english_review, rating)

    return {
        "sentiment": result["label"],
        "rating": rating,
        "aspects": aspects
    }