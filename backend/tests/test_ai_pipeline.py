import pytest
from app.services.embedder import embedder
from app.services.crisis_service import is_crisis_message
from app.config import settings

@pytest.fixture(scope="module", autouse=True)
def init_embedder():
    # Make sure embedder is initialized and corpus is loaded
    if not embedder._loaded:
        embedder.initialize()
        embedder.load_corpus(settings.CORPUS_PATH)

def test_relevance_check():
    # Mental health related queries should be relevant (>= 0.25)
    rel_queries = [
        "I feel so anxious and overwhelmed today",
        "I'm feeling really depressed and lonely",
        "I cannot sleep because of stress"
    ]
    for q in rel_queries:
        vec = embedder.embed(q)
        is_rel, score = embedder.check_relevance(vec)
        assert is_rel is True, f"Failed relevance check for: '{q}' (score: {score})"

    # Off-topic queries should be irrelevant (< 0.25)
    irrel_queries = [
        "How to compile a C++ program?",
        "What is the capital of France?",
        "Show me a recipe for chocolate cake"
    ]
    for q in irrel_queries:
        vec = embedder.embed(q)
        is_rel, score = embedder.check_relevance(vec)
        assert is_rel is False, f"Failed irrelevance check for: '{q}' (score: {score})"

def test_crisis_keyword_detection():
    # Crisis keywords should trigger is_crisis_message
    crisis_queries = [
        "I want to kill myself",
        "I'm thinking of suicide",
        "I feel like self harm"
    ]
    for q in crisis_queries:
        assert is_crisis_message(q) is True, f"Failed crisis keyword check for: '{q}'"

    # Non-crisis queries should not trigger keyword check
    safe_queries = [
        "I am stressed about my exams",
        "I had a bad day at work"
    ]
    for q in safe_queries:
        assert is_crisis_message(q) is False, f"Failed non-crisis keyword check for: '{q}'"

def test_crisis_embedding_detection():
    # High-intensity crisis messages should trigger check_crisis_embedding (>= 0.7)
    # E.g. semantically close to suicide/self-harm
    crisis_queries = [
        "I want to end my life right now",
        "thinking about hurting myself"
    ]
    for q in crisis_queries:
        vec = embedder.embed(q)
        assert embedder.check_crisis_embedding(vec) is True, f"Failed crisis embedding check for: '{q}'"

def test_few_shot_retrieved_count():
    # Should retrieve exactly TOP_K (3) examples
    vec = embedder.embed("I feel lonely")
    examples = embedder.get_few_shot_examples(vec)
    assert len(examples) == 3
    # Check that they have context and response keys
    for ex in examples:
        assert "context" in ex
        assert "response" in ex
