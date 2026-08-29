"""
Quick demo: shows the trained classifier's category prediction + confidence
for a handful of test messages, without going through the full Gemini
pipeline. Good for a live demo moment in your review.

Run from backend/:
    venv\\Scripts\\activate
    python scripts\\test_classifier_demo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.embedder import embedder
from app.services.classifier_service import classifier_service
from app.config import settings

TEST_MESSAGES = [
    "I can't stop worrying about my exam results",
    "I feel so alone even when I'm surrounded by people",
    "My partner and I keep having the same fight over and over",
    "I lost my grandmother last month and I still cry every day",
    "I snapped at my sister today and I feel terrible about it",
    "I haven't slept properly in over a week",
    "I don't think I can keep going anymore",
    "yes",  # short/ambiguous input — the original weak spot
    "I don't know",  # short/ambiguous input
]


def main():
    print("Loading models (this takes a few seconds)...\n")
    embedder.initialize()
    embedder.load_corpus(settings.CORPUS_PATH)
    classifier_service.initialize()

    if not classifier_service._loaded:
        print("No trained classifier found — run scripts/train_classifier.py first.")
        return

    print("\n" + "=" * 70)
    print(f"{'Message':<45} {'Category':<15} {'Conf.':<8} {'Uncert.'}")
    print("=" * 70)

    for msg in TEST_MESSAGES:
        query_vec = embedder.embed(msg)
        result = classifier_service.predict(query_vec)

        display_msg = (msg[:42] + "...") if len(msg) > 42 else msg
        print(
            f"{display_msg:<45} "
            f"{result['category']:<15} "
            f"{result['confidence']:.3f}   "
            f"{result['uncertainty']:.4f}"
        )

    print("=" * 70)
    print("\nNote: 'Conf.' is the model's confidence in its top category guess")
    print("(via MC Dropout, averaged over 20 passes). 'Uncert.' is the variance")
    print("across those passes — higher means the model is less sure.")


if __name__ == "__main__":
    main()
