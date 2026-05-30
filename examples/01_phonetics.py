"""Look up the IPA / AFI transcription of a Portuguese word."""
import pyportaldalingua as pdl


def main() -> None:
    for word in ("palavra", "acasalado", "computador"):
        ipa = pdl.phonetics(word)
        print(f"{word:14} {ipa}")


if __name__ == "__main__":
    main()
