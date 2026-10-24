## What it does

`sc-governed-task` gets an agent to make a change with stAirCase deciding every step. The assistant prepares the exact command, you run it in your own terminal and approve in it, and the assistant checks the result afterwards. The change is committed on a branch, `staircase/run-N`, and your own checkout is untouched while the agent works.

It never starts the run for you and never answers the prompts. It offers three modes and says what each gives up: every change by hand, in-scope changes as part of the task, or on evidence from the checks.

## When to reach for it

Type `/sc-governed-task`, or the assistant reaches for it when you want to run Claude Code, Codex, Gemini CLI or OpenCode on a task, choose how much to approve, review the branch a run produced, throw a run away, or continue an interrupted one.

| Your situation | Where to go |
|---|---|
| You are at the keyboard and want a change made | `sc-governed-task` |
| You want to start and leave | [sc-away-run](sc-away-run.md) |
| The agent runs outside stAirCase | [sc-review-and-seal](sc-review-and-seal.md) |
| A run ended failed or stuck | [sc-investigate-run](sc-investigate-run.md) |

## Prerequisites

The repository needs at least one commit. The agent works on the last commit, so uncommitted files and ignored paths are not in its copy. A project with checks or secrets should be onboarded first with [sc-onboard-project](sc-onboard-project.md).

## It's working if

- You are given a command to run, not a run that already started.
- The choice of mode came with what it gives up.
- Afterwards you can read the change with `git diff HEAD...staircase/run-N`, and `staircase verify` accepts the branch.
- The story is marked done by you, with the command the run printed.

## Where it fits

The middle of the main flow: [sc-onboard-project](sc-onboard-project.md), then this, then a merge and [sc-ci-verify](sc-ci-verify.md). The map of every skill is [sc-ask](sc-ask.md).
