"""Export both HF dataset configs: the IPA corpus and the AO change set."""
import pyportaldalingua as pdl
from pyportaldalingua import dataset


def main() -> None:
    lemmas = pdl.lemmas("casa")
    changes = pdl.load_changes_csv("pt_PT")
    counts = dataset.export_all(lemmas, changes, "corpus/")
    print("wrote:", counts)   # {'ipa': N, 'acordo': M}


if __name__ == "__main__":
    main()
