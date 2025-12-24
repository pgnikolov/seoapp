import pytest
from app.utils.url import normalize_url, is_same_domain, is_valid_url
from app.services.analyzer import KeywordAnalyzer

def test_normalize_url():
    assert normalize_url("https://example.com/path/") == "https://example.com/path"
    assert normalize_url("/subpage", "https://example.com") == "https://example.com/subpage"
    assert normalize_url("https://example.com/path#fragment") == "https://example.com/path"
    assert normalize_url("HTTPS://EXAMPLE.COM") == "https://example.com/"

def test_is_same_domain():
    assert is_same_domain("https://example.com", "https://example.com/page") is True
    assert is_same_domain("https://example.com", "https://sub.example.com") is False
    assert is_same_domain("https://example.com", "https://sub.example.com", include_subdomains=True) is True

def test_ngram_generation():
    analyzer = KeywordAnalyzer([])
    text = "this is a test sentence"
    clean = analyzer.clean_text(text)
    
    unigrams = analyzer.generate_ngrams(clean, 1)
    assert "test" in unigrams
    assert len(unigrams) == 5
    
    bigrams = analyzer.generate_ngrams(clean, 2)
    assert "test sentence" in bigrams
    assert len(bigrams) == 4

def test_intent_heuristic():
    analyzer = KeywordAnalyzer([])
    assert analyzer.get_intent("buy cheap iphone") == "commercial"
    assert analyzer.get_intent("how to fix a car") == "informational"
    assert analyzer.get_intent("contact us") == "navigational"

def test_scoring_logic():
    pages = [
        {
            "url": "https://example.com",
            "title": "SEO Tool",
            "h1": ["Best SEO Tool"],
            "body": "This is a great seo tool for keywords.",
            "links": []
        }
    ]
    analyzer = KeywordAnalyzer(pages, target_lang='en')
    results = analyzer.analyze()
    
    assert len(results) > 0
    # "seo tool" should have high score because it is in title and h1
    top_keyword = results[0]
    assert "seo tool" in top_keyword['phrase']
    assert top_keyword['score'] == 100.0
