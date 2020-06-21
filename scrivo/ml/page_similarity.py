"""Compute text similarity between Pages."""

import logging
import re
from typing import Dict, List

import numpy as np
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from snowballstemmer import EnglishStemmer

from scrivo.page import Page
from scrivo.utils import logtime

STEMMER = EnglishStemmer()

logger = logging.getLogger(__name__)


# Get a plaintext rendering of a page
def get_page_plaintext(p: Page) -> str:
    """Return a plaintext page rendering for tokenization."""
    # Bit of a hack, but throw in any tags and the page title
    title_text = p.meta["title"]
    tags_text = " ".join(p.meta["tags"])
    page_text = BeautifulSoup(p.html, features="html.parser").get_text(
        separator=" ", strip=True
    )
    return " ".join([title_text, tags_text, page_text])


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
@logtime
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
        # Sort by similarity, descending, but track indices to match to pages
        vec = similarity[:, i].toarray().reshape(-1)
        indices = np.argsort(-vec)
        # Mask out nonzero results
        nonzero_indices = np.argwhere(vec > 0).reshape(-1)
        indices = indices[np.isin(indices, nonzero_indices)]
        # Build the final dict
        result[page] = {vec[j]: pages[j] for j in indices if pages[j] != page}

    return result
