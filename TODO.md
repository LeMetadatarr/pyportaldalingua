# TODO — pyportaldalingua

## Gaps

- [ ] No CI workflows — `.github/workflows/` is intentionally absent. Add the
  standard gh-automations reusable workflows (build-tests, coverage,
  license-check, release_workflow, publish_stable), referencing
  `OpenVoiceOS/gh-automations` at `@dev`.
- [ ] No lint/typecheck config — no ruff/mypy despite full type-hint usage.

## Coverage ideas

- [ ] Parse the portal's `action=lemma&id=<N>` page (linked from the phonetic
  detail) for fuller grammatical / inflection data.
- [ ] Expose the proverbs (`data/proverbios.txt`) and loanwords
  (`data/estrangeirismos.pdf`) as their own readers / dataset configs.
- [ ] Map the `acordo` change rows against the `ao`/`preao` word-lists to flag
  every word a reform spelling actually touches.
- [ ] Resolve multi-word lemma headwords (e.g. "cabeça de casal") without
  collapsing the spaces, when a caller needs the surface form.

## Code TODOs

None found.
