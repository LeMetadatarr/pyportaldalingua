"""Fetch a lemma's IPA in every transcribed regional accent."""
import pyportaldalingua as pdl


def main() -> None:
    lm = pdl.phonetics_detail("palavra")
    if lm is None:
        print("no phonetic entry")
        return
    print(f"{lm.word} ({lm.grammatical_class}) — syllables {lm.syllabification}")
    for region, ipa in lm.ipa_by_region.items():
        print(f"  {region:30} {ipa}")


if __name__ == "__main__":
    main()
