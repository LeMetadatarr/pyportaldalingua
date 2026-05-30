"""HF-publishable dataset export for the portal corpora.

Two streaming configs derive from the portal's two resources:

``ipa``
    One row per lemma with a transcription: ``word, ipa, syllables, class,
    source`` — **the Portuguese IPA pronunciation dataset**, the training signal
    for grapheme-to-phoneme and TTS front-ends. Built from :class:`Lemma`
    objects (live :func:`pyportaldalingua.lemmas` / detail fetches).

``acordo``
    One row per Acordo Ortográfico de 1990 change: ``old, new, variant, note,
    source`` — the AO90 pt_PT/pt_BR change set. Built from :class:`AOChange`
    objects (the bundled CSVs or a live scrape).

Rows are written as JSON Lines (one object per line), loadable directly with
``datasets.load_dataset("json", ...)`` and streamable without holding the corpus
in memory. :func:`export_jsonl` writes one config; :func:`export_all` writes both
plus a manifest. :func:`build_ipa_corpus` crawls a set of words into the ``ipa``
config; :func:`build_acordo_corpus` exports the AO change set.

The output is a Portuguese grapheme-to-phoneme (IPA) supervision corpus for
pronunciation modelling and phonemics research — see ``docs/dataset.md``.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from pyportaldalingua import orthography, phonetics
from pyportaldalingua.models import AOChange, Lemma
from pyportaldalingua.transport import Transport, default_transport

CONFIGS = ("ipa", "acordo")
SOURCE = "portaldalinguaportuguesa.org"


def ipa_row(lemma: Lemma) -> Optional[dict]:
    """Row for the ``ipa`` config, or ``None`` when the lemma has no IPA."""
    if not lemma.ipa:
        return None
    return {
        "word": lemma.word,
        "ipa": lemma.ipa,
        "syllables": list(lemma.syllables),
        "class": lemma.grammatical_class,
        "source": SOURCE,
    }


def acordo_row(change: AOChange) -> dict:
    """Row for the ``acordo`` config."""
    return {
        "old": change.old,
        "new": change.new,
        "variant": change.variant,
        "note": change.note,
        "source": SOURCE,
    }


def export_jsonl(items: Iterable, path: str, config: str = "ipa") -> int:
    """Write one config to a JSONL file. Returns the number of rows written.

    Args:
        items:  iterable of :class:`Lemma` (``ipa``) or :class:`AOChange`
                (``acordo``).
        path:   output ``.jsonl`` path.
        config: ``"ipa"`` or ``"acordo"``.
    """
    if config not in CONFIGS:
        raise ValueError(f"unknown config {config!r}; expected one of {CONFIGS}")
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(out, "w", encoding="utf-8") as fh:
        for item in items:
            row = ipa_row(item) if config == "ipa" else acordo_row(item)
            if row is None:
                continue
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    return n


def export_all(lemmas: Iterable[Lemma], changes: Iterable[AOChange],
               out_dir: str) -> Dict[str, int]:
    """Write both configs under *out_dir* as ``<config>.jsonl`` plus a manifest.

    Returns a ``{config: row_count}`` summary.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    counts = {
        "ipa": export_jsonl(lemmas, str(out / "ipa.jsonl"), "ipa"),
        "acordo": export_jsonl(changes, str(out / "acordo.jsonl"), "acordo"),
    }
    (out / "manifest.json").write_text(
        json.dumps({"configs": counts}, indent=2), encoding="utf-8")
    return counts


def build_ipa_corpus(out_path: str, words: Iterable[str], *,
                     detail: bool = False, delay: float = 1.0,
                     transport: Optional[Transport] = None) -> int:
    """Crawl the Dicionário Fonético for *words* and export the ``ipa`` config.

    With ``detail=False`` (default) each word costs one search request and the
    standard IPA is kept. With ``detail=True`` a detail page is also fetched and
    the row's IPA stays the standard form (per-region IPA lives on the Lemma).
    Polite: one shared transport, a delay between words. Returns the row count.
    """
    t = transport or default_transport()
    words = list(words)
    found: List[Lemma] = []
    for i, w in enumerate(words):
        try:
            if detail:
                lm = phonetics.phonetics_detail(w, transport=t)
                if lm is not None:
                    found.append(lm)
            else:
                low = w.strip().lower()
                for lm in phonetics.lemmas(w, transport=t):
                    if lm.word.lower() == low and lm.ipa:
                        found.append(lm)
                        break
        except Exception:
            pass
        if delay and i < len(words) - 1:
            time.sleep(delay)
    return export_jsonl(found, out_path, "ipa")


def build_acordo_corpus(out_path: str, *, variant: str = "pt_PT",
                        from_csv: bool = True,
                        transport: Optional[Transport] = None) -> int:
    """Export the ``acordo`` config for *variant*. Uses the bundled CSV by
    default; set ``from_csv=False`` to scrape the portal live."""
    if from_csv:
        changes = orthography.load_changes_csv(variant)
    else:
        changes = orthography.scrape_variant(variant, transport=transport)
    return export_jsonl(changes, out_path, "acordo")
