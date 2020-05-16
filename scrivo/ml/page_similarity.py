"""Compute text similarity between Pages."""

import re
from typing import Dict, List

import numpy as np
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from snowballstemmer import EnglishStemmer

from scrivo.page import Page

STEMMER = EnglishStemmer()


# Get a plaintext rendering of a page
def get_page_plaintext(p: Page) -> str:
    """Return a plaintext page rendering for tokenization."""
    return BeautifulSoup(p.html, features="html.parser").get_text(
        separator=" ", strip=True
    )


def tokenize_stop_stem(doc: str) -> List[str]:
    """Tokenize, stop, _and_ stem a document.

    Same tokenizer and stop words as sklearn, but with snowball stemming.
    """
    # From TfidfVectorizer.__init__()
    PATTERN = re.compile(r"(?u)\b\w\w+\b")
    return STEMMER.stemWords(
        t for t in PATTERN.findall(doc) if t not in ENGLISH_STOP_WORDS
    )


# Compute the TF-IDF for a collection of Pages
def page_similarities(pages: List[Page]) -> Dict[Page, Dict[float, Page]]:
    """Calculate TF-IDF page similarities between all pages.

    Args:
        pages (list[Page]): the full collection of pages

    Returns:
        (dict[Page, dict[float, Page]]): a dict, keyed by Page, that
          maps similar pages. The values are dicts keyed by the
          similarity value for easy processing.
    """
    # Compute the similarities
    texts = map(get_page_plaintext, pages)
    tfidf = TfidfVectorizer(
        tokenizer=tokenize_stop_stem, stop_words=None, ngram_range=(1, 1)
    )
    mat = tfidf.fit_transform(texts)
    similarity = mat @ mat.T
    # Return a descending-ordered set of nonzero similarities
    result = {}
    for i, page in enumerate(pages):
        # Get nonzero entries and indices, sorted by similarity
        vec = similarity[:, i].toarray().reshape(-1)
        indices = np.argsort(-vec)
        vec = vec[indices]
        indices = np.argwhere(vec > 0.001).reshape(-1)
        result[page] = {vec[j]: pages[j] for j in indices if pages[j] != page}
    return result
