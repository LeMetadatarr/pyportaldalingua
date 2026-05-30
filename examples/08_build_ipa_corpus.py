"""Seed a Portuguese IPA corpus from the bundled word-list (polite crawl)."""
import itertools

import pyportaldalingua as pdl
from pyportaldalingua import dataset


def main() -> None:
    words = itertools.islice(pdl.load_wordlists("ao"), 25)
    n = dataset.build_ipa_corpus("ipa.jsonl", words, delay=1.0)
    print(f"wrote {n} IPA rows to ipa.jsonl")


if __name__ == "__main__":
    main()
