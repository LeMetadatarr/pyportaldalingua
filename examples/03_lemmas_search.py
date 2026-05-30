"""List every lemma the phonetic dictionary indexes for a search term."""
import pyportaldalingua as pdl


def main() -> None:
    for lm in pdl.lemmas("casa"):
        print(f"{lm.word:24} {lm.grammatical_class or '':10} {lm.ipa}")


if __name__ == "__main__":
    main()
