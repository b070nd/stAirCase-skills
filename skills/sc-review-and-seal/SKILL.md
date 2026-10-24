---
name: sc-review-and-seal
description: Certify changes that an AI agent made outside stAirCase, so only the files a person approves are committed. Use when the user has a cloud agent's pull request or branch (Copilot coding agent, Codex in the cloud) to review, or an agent that edits their own checkout (Cursor, an IDE assistant) and wants to commit only what they approve, with a change certificate.
---

# Review after, and seal

Call the Skill tool with "sc-basics" first, unless it was loaded earlier in this conversation: it holds the rules every stAirCase skill follows.

Some agents work where stAirCase cannot decide their steps before they happen. stAirCase can still make sure that only the files the user approves are committed, and certify it. Both routes reach **CAL 2**: every byte that lands was decided, but nobody governed what the agent did on its own machine. For CAL 3 the agent has to run through stAirCase (`sc-governed-task`).

## A cloud agent's branch or pull request: `staircase review`

The user runs these in their terminal. Fetch the branch, then review it:

```bash
git fetch origin pull/42/head:pr-42
staircase review pr-42 --by "Copilot coding agent" --check "go test ./..."
```

stAirCase shows what is about to be reviewed and asks to confirm. It makes a separate worktree of the current branch and brings the branch's own changes in one file at a time, so newer work on the current branch is kept. A file whose change no longer fits is left out and reported. Each file comes to the person to approve or reject; rejected files are left out. Exactly the approved files are committed on `staircase/run-N` with an `Assisted-by:` trailer and a signed certificate. `--allow` limits where changes may go: a file elsewhere comes to the person as drift.

## An agent in the user's own checkout: `staircase attach` and `staircase seal`

Cursor, IDE assistants and any tool stAirCase has no hooks for edit the checkout directly.

```bash
staircase attach
git add -p
staircase seal -m "Add the health endpoint" --by "Cursor" --check "go test ./..."
staircase attach --off
```

`attach` installs a pre-commit hook that refuses a plain `git commit` and says to seal. It is not a wall: `git commit --no-verify` gets through, which is why CI (`sc-ci-verify`) is the second line. Nothing of stAirCase is written into the repository's files: if `core.hooksPath` points inside the working tree (a `.husky` folder, say), `attach` refuses and names the setting.

`seal` takes exactly what is staged. Each staged file comes to the person, and the current branch moves to one new commit with the approved files, the message, the `Assisted-by:` trailer and a certificate. Rejected changes are not committed and not thrown away: they stay in the working files. Edits that were not staged are left alone. If the branch moved while the person was deciding, it is not touched and the certified commit stays on `staircase/run-N`. `seal` takes `--allow` like the other commands.

## Notes

- `--check` runs in a throwaway checkout of the new commit, not in the working directory. That checkout holds tracked files only, so a check that needs an ignored directory such as `vendor/` cannot pass there, even with `--sandbox off`.
- A second person can sign a reviewed change with `staircase sign`, but CAL 4 needs CAL 3 first, so a reviewed or sealed change stays at CAL 2.
