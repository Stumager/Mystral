# -*- coding: utf-8 -*-
"""Group B (QA-015): AI-streamed text lost Latin diacritics for ES/PT/TR
because the per-chunk allow-list only kept ASCII + Cyrillic. groq_client's
_clean_chunk allow-list now spans Latin-1 Supplement + Latin Extended
(U+00A1..U+024F), and the frontend streamRequest cleaner mirrors it. These
tests lock in the backend half of that contract: target-language letters and
Spanish inverted punctuation survive, while genuinely foreign scripts (the
reason the filter exists — models occasionally emit stray CJK) are stripped.
"""
from app.core.groq_client import _clean_chunk


class TestCleanChunkPreservesTargetLanguages:
    def test_portuguese_accents_survive(self):
        assert _clean_chunk("não vou à reunião") == "não vou à reunião"

    def test_turkish_letters_survive(self):
        assert _clean_chunk("gün içinde çalışır") == "gün içinde çalışır"
        assert _clean_chunk("ĞğİıŞşÖöÜüÇç") == "ĞğİıŞşÖöÜüÇç"

    def test_spanish_accents_and_inverted_punctuation_survive(self):
        assert _clean_chunk("¿Qué pasa? ¡Corazón!") == "¿Qué pasa? ¡Corazón!"
        assert _clean_chunk("señor niño") == "señor niño"

    def test_ukrainian_cyrillic_survives(self):
        assert _clean_chunk("Привіт, світ! Ґіґ їжак") == "Привіт, світ! Ґіґ їжак"

    def test_russian_and_english_unaffected(self):
        assert _clean_chunk("Овен: сегодня day") == "Овен: сегодня day"


class TestCleanChunkStripsForeignScripts:
    def test_cjk_stripped(self):
        assert _clean_chunk("hello 日本語 world") == "hello  world"

    def test_arabic_stripped(self):
        assert _clean_chunk("test مرحبا x") == "test  x"
