"""Stream the bundled word-lists (post-AO90, pre-AO90, combined)."""
import itertools

import pyportaldalingua as pdl


def main() -> None:
    for key in pdl.wordlist_names():
        head = list(itertools.islice(pdl.load_wordlists(key), 8))
        print(f"{key:6} {head}")


if __name__ == "__main__":
    main()
