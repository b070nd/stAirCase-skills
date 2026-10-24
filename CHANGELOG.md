# Changelog

## [0.2.0] - unreleased

Changed

- Every skill is named `sc-<name>`: `sc-basics` (was `staircase`), `sc-onboard-project`, `sc-governed-task`, `sc-away-run`, `sc-review-and-seal`, `sc-ci-verify`, `sc-investigate-run`, `sc-change-set` and `sc-policy-rules`. The short prefix keeps the typed names unique.
- `sc-away-run` and `sc-policy-rules` are started by the person only (`disable-model-invocation`), because they set how much a person reads or write a standing rule.
- The skills call `sc-basics` first, with the Skill tool, instead of repeating its rules.

Added

- `sc-ask`, a router over every skill and how they fit together, started by the person.
- `sc-setup`, which records the agent, the CI system and whose repository it is in a short block of notes. For a client's repository the notes go in `CLAUDE.local.md`, excluded through `.git/info/exclude`, so the repository is not changed.
- A docs page for every skill in `docs/`.
- Checks that the set stays whole: the `sc-` prefix, the router, the README links, the docs sections, how person-only skills are named, and that docs pages show only real `staircase` commands.

## [0.1.0] - 2026-10-24

First version: nine skills for stAirCase v1.3.0.

- `staircase`: orientation, and the rules every skill follows (the decisions belong to the person).
- `onboard-project`, `governed-task`, `away-run`, `review-and-seal`, `ci-verify`, `investigate-run`, `change-set`, `policy-rules`.
- A check (`tools/check_skills.py`) that every `staircase` command and flag in a skill exists in the release named in `STAIRCASE_VERSION`.
