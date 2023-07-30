"""Compute page-page similarities."""

from scrivo.pages import page


def tf_similarity(pages: list[page]) -> list[float]:
    return [1.0]


def tfidf_similarity(pages: list[page]) -> list[float]:
    return [1.0]


def embedding_similarity(pages: list[page]) -> list[float]:
    return [1.0]
