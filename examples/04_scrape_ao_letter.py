"""Scrape the Acordo Ortográfico changes for one letter, both variants."""
import pyportaldalingua as pdl


def main() -> None:
    for variant in ("pt_PT", "pt_BR"):
        changes = pdl.scrape_letter("a", variant)
        print(f"{variant}: {len(changes)} changes for 'a'")
        for ch in changes[:5]:
            print(f"  {ch.old} -> {ch.new}")


if __name__ == "__main__":
    main()
