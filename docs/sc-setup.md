## What it does

`sc-setup` writes a short block of notes about the project that the other skills read: which agent you run, where CI runs, and the rule that modes which make a person read less are never chosen for them. It also checks that stAirCase is installed and which release it is.

It asks whose repository this is before it writes anything, because that decides where the notes go. In a client's or employer's repository nothing of stAirCase goes into the repository: the notes go in `CLAUDE.local.md`, which is excluded through `.git/info/exclude`, so no tracked file changes.

## When to reach for it

You type `/sc-setup`. The assistant never starts it on its own. Reach for it once per project, before the first flow. Run it again only to change the agent or the CI system.

## Prerequisites

stAirCase installed and on the path. `staircase doctor` says what is missing.

## Common questions

**Why does it not write into `CLAUDE.md` of a client's repository?**

Because that file is tracked, and a client's repository should not learn that you use stAirCase. `CLAUDE.local.md` is yours alone.

**Does it set up the project profile?**

No. The profile (checks, scope, protected files) is the job of [sc-onboard-project](sc-onboard-project.md), which `sc-setup` hands over to at the end.

## It's working if

- You were asked whose repository it is before any file was written.
- It names the one file it wrote, and says nothing else was changed.
- For a client's repository, `git status` shows no change and `.git/info/exclude` lists `CLAUDE.local.md`.

## Where it fits

A run-once setup, the first step of the main flow. It is followed by [sc-onboard-project](sc-onboard-project.md). The map of every skill is [sc-ask](sc-ask.md).
