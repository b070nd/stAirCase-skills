## What it does

`sc:policy-rules` writes, tests and signs `policy.json`, the rules that approve or reject some kinds of change without asking. A rule is your decision made in advance, so each one is written narrowly. Rules are checked in order and the first match decides. They never read a change, they match what stAirCase derived from it.

It tests the file against every proposal recorded in the workspace before use, and reads you first the changes a person rejected that the policy would approve: each is a rule that is too wide.

A rule can never approve a shell command or a tool call, and never widens what already needs a person, such as protected and sensitive paths.

## When to reach for it

You type `/sc:policy-rules`. The assistant never starts it on its own, because it writes standing decisions. Reach for it when you want small or safe changes approved automatically, a path or an agent rejected, or a policy tested or signed.

## Prerequisites

Past runs in the workspace, so `staircase policy test` has something to replay. Delivery by policy also needs a signed policy and the conditions described in [sc:away-run](away-run.md).

## Common questions

**Why did a run stop with `policy integrity check failed`?**

The file changed after it was signed. If you made the change, sign again with `staircase policy sign`.

**Why will an older stAirCase not load my policy?**

The change conditions (`paths`, `max_lines`, `max_files`, `new_files_only`, `no_deletions`) are refused by an older release on purpose, so a rule is never read as wider than written.

## It's working if

- Every rule you approved was shown with what it will approve.
- `staircase policy test` was read, and the section of rejected-but-approved changes is empty or explained.
- `staircase policy verify` passes after signing.

## Where it fits

Automation beside the main flow. It makes delivery by policy possible for [sc:away-run](away-run.md). The map of every skill is [sc:ask](ask.md).
