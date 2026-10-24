## What it does

`sc-away-run` starts a task and lets you leave. An away run asks nobody. A change is approved only when your checks pass on the exact state it would produce, and anything that needs a person is parked, not asked. Nothing is committed: the run waits for `staircase decide`, which shows you one tree per run when you are back.

It also covers what away runs leave behind: a parked change, a blocked run, a run whose agent was lost, and delivery by policy.

## When to reach for it

You type `/sc-away-run`. The assistant never starts it on its own, because it sets how much a person reads. Reach for it when you want an agent to work while you are away, or when you come back to runs that are waiting.

| Your situation | Where to go |
|---|---|
| Start a task and leave | `sc-away-run` |
| You are at the keyboard | [sc-governed-task](sc-governed-task.md) |
| A run ended failed, or its record looks wrong | [sc-investigate-run](sc-investigate-run.md) |
| Approve some changes by rule | [sc-policy-rules](sc-policy-rules.md) |

## Prerequisites

At least one `--check`, and checks that can pass on each intermediate state. A build, a linter and fast tests work. A suite that fails until three files exist does not.

## Common questions

**Why was my change parked?**

Shell commands, MCP tools, and changes to protected or sensitive paths are always parked in an away run. A command you can name in advance can be declared with `--away-command`.

**Does delivery by policy mean nobody reads the change?**

Yes. `--deliver policy` commits to the run branch with no person reviewing the whole change, only when seven conditions hold. The skill describes it and leaves the choice to you.

## It's working if

- You were told what the run cannot decide, and what a declared command or tool gives up.
- `--away` came with a `--check`, and the paths that define the checks are protected.
- When you are back, `staircase decide` shows each waiting run with the checks that ran on exactly that change.
- Nothing was accepted until you said which run and which way.

## Where it fits

An alternative to the at-the-keyboard step of the main flow, followed by `staircase decide`. Its neighbour is [sc-policy-rules](sc-policy-rules.md), whose signed rules make delivery by policy possible. The map of every skill is [sc-ask](sc-ask.md).
