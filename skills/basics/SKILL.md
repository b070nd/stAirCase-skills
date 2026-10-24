---
name: basics
description: What stAirCase is and the rules every stAirCase skill follows. Use when the user mentions stAirCase or staircase, governed or certified agent runs, approving what an agent changes, change certificates, or asks how to start with it.
---

# stAirCase basics

stAirCase runs an AI coding agent in a separate worktree. Every change the agent wants to make comes to a person first. At the end, exactly the approved bytes are committed on a new branch, `staircase/run-N`, with a signed change certificate and a hash-chained audit record that anyone can verify. The person's own checkout is not touched while the agent works.

## The rule behind every skill here

**The decisions belong to the person.** You prepare, explain and inspect. You do not decide.

- Never approve, reject or accept something because it looks fine. Run `staircase decide <run> --accept` or `--reject` only when the user told you, in this conversation, which run and which way, and put their words in `-m`.
- Interactive commands ask the person y or n: `staircase claude`, `codex`, `gemini`, `opencode`, `run`, `review`, `seal`. Give the user the exact command to run in their own terminal. Do not run it yourself, and do not answer its prompts. Do not add `-y` to skip the confirmation unless the user asks for a script.
- Modes that make a person read less are the user's choice, not yours: `--approve-in-scope`, `--approve-on-evidence`, `--away`, `--deliver policy`. Offer them, say plainly what each gives up, and let the user pick.
- Secrets: `staircase secret set` reads the value from standard input. Never put a key on a command line, in a file of the repository, or in output you show. Write `<REDACTED>`.
- Nothing of stAirCase goes into a client's repository. A project's settings live in the workspace (`staircase project profile`), not in files of the repository.
- Never edit the workspace by hand (database, keys, audit files), and never repair a broken audit chain. Stop and tell the user.

## Commands you may run freely

These read and change nothing: `staircase version`, `staircase doctor`, `staircase inspect runs`, `staircase inspect log <run>`, `staircase replay <run>`, `staircase verify <commit>`, `staircase case briefing <case-id>`, `staircase project profile show <id>`, `staircase changeset show <id>`, `staircase policy test <file>`, and `staircase decide` with no run id in a tool that has no terminal (it lists what waits and asks nothing).

## Which skill

The other skills pick themselves from what the user asks. For the whole map, tell the user to run `/sc:ask`. For a project that has not been set up for these skills, tell them to run `/sc:setup`.

## First, every time

```bash
staircase version
staircase doctor
```

These skills were checked against one release of stAirCase: the file `STAIRCASE_VERSION` in this plugin names it. If `staircase version` prints another, read `staircase <command> --help` before you trust a flag.

The documentation is at https://github.com/b070nd/stAirCase/blob/master/docs/README.md.
