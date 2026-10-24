---
name: ask
description: Ask which stAirCase skill or flow fits your situation. A router over the skills in this plugin.
disable-model-invocation: true
---

# Ask stAirCase

You don't remember every skill, so ask.

Before stating what a skill does or advising a step be skipped, read that skill's SKILL.md: the summaries here are for orientation only.

A **flow** is a path through the skills. Most work runs along one **main flow**. Two on-ramps and a few standalone skills sit beside it.

## The main flow: task to merged

You have a change to make and want a person's decision on every part of it.

1. **`/sc:setup`** once per project. It records which agent you use, where CI runs and whether the repository is yours or a client's, in a short block of notes the assistant reads.
2. **`sc:onboard-project`** makes the project profile: the checks, the scope, the protected and sensitive files, the files an agent must not read, the house rules. Do it before the first run on any project that has tests or secrets.
3. **`sc:governed-task`** runs one agent on one task with you deciding. Pick how much you decide by hand: every change, in-scope changes as part of the task, or on evidence from checks.
4. **Branch: will you be at the keyboard?**
   - **Yes**: you approve in the run itself.
   - **No**: **`/sc:away-run`** starts the task and lets you leave. Anything that needs a person is parked, and `staircase decide` puts one decision in front of you when you are back.
5. The approved changes are on `staircase/run-N`. Merge the branch as usual, or `staircase push` opens a pull request.
6. **`sc:ci-verify`** makes CI refuse commits an agent helped make without a valid change certificate.

## On-ramps

A starting situation that merges onto the main flow.

- **The agent does not run through stAirCase** (a cloud agent's pull request, Cursor or an IDE assistant in your checkout) → **`sc:review-and-seal`**. It certifies exactly the files you approve, at CAL 2. For CAL 3 the agent has to run through `sc:governed-task`.
- **One change across several repositories** → **`sc:change-set`**. One governed task per repository, tied by an id, then one command that verifies them together, including the contracts between repositories.

## When something is wrong

- **A run failed, is stuck, was killed, or its record looks wrong** → **`sc:investigate-run`**. It only reads. It explains the outcome, gives the command that continues or recovers the run, and stops when the audit chain is broken.

## Automation

- **`/sc:policy-rules`** writes, tests and signs the rules that approve or reject some kinds of change without asking. A rule is your decision made in advance, so the skill tests it against your past runs first.
- Rules are what lets `/sc:away-run` deliver by policy, with nobody reading the change. Only for work a rule really decides, such as documentation.

## Underneath

- **`sc:basics`** is what stAirCase is and the rules every skill follows: the decisions belong to the person, interactive commands run in your own terminal, nothing of stAirCase goes into a client's repository, a broken audit chain is never repaired. The other skills load it themselves.

## Precondition

**`/sc:setup`**: run it once in each project before the first flow.

## Which skills you type, and which the assistant reaches for

| You type | The assistant reaches for it when a task fits |
|---|---|
| `/sc:ask`, `/sc:setup`, `/sc:away-run`, `/sc:policy-rules` | `sc:basics`, `sc:onboard-project`, `sc:governed-task`, `sc:review-and-seal`, `sc:ci-verify`, `sc:investigate-run`, `sc:change-set` |

The ones you type are the ones that set how much a person reads or that write standing rules. The assistant never starts them on its own.
