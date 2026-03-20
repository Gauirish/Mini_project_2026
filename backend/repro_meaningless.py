import sys
import os

# Dummy sentiment model to avoid loading weights
import transformers
orig_pipeline = transformers.pipeline
transformers.pipeline = lambda *args, **kwargs: None

from model import is_meaningless

test_cases = [
    "This movie was power packed and quiet good.",
    "The glass work in the visuals was amazing.",
    "The route the story took was very quiet.",
    "It falls short of expectations.",
    "I shall watch it again.",
    "The rhythm of the music was great.",
    "Psychology of the characters was deep.",
    "It was a cool movie.",
]

for test in test_cases:
    meaningless, msg = is_meaningless(test)
    print(f"Review: {test}")
    print(f"Meaningless: {meaningless}")
    if meaningless:
        print(f"Message: {msg}")
    print("-" * 20)
