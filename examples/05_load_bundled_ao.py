"""Load the pre-built Acordo Ortográfico change set from the bundled CSVs."""
import pyportaldalingua as pdl


def main() -> None:
    pt = pdl.load_changes_csv("pt_PT")
    br = pdl.load_changes_csv("pt_BR")
    print(f"pt_PT changes: {len(pt)}")
    print(f"pt_BR changes: {len(br)}")
    print("sample pt_PT:", pt[0].old, "->", pt[0].new)


if __name__ == "__main__":
    main()
