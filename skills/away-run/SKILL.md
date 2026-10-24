---
name: away-run
description: Start a stAirCase task and leave, then come back to one decision, or deal with what away runs left. Use when the user wants an agent to work while they are away, set up declared commands or tools for an unattended run, review runs with staircase decide, handle a run that is parked, blocked or lost, or asks about delivery by policy.
---

# Away runs

An away run asks nobody. A change is approved only when the user's checks pass on the exact state it would produce. Anything that needs a person is **parked**, not asked, and the agent is told to carry on without it. At the end the checks run once more on the whole approved change. Nothing is committed: the run waits for `staircase decide`.

## Start one (the user runs it)

`--away` needs at least one `--check`. Give the user a command like this for their terminal:

```bash
staircase claude "add a /health endpoint with a test" --allow "src/**" --away --check "go test ./..."
```

Points to settle first:

- The checks must be able to pass on each intermediate state, or most changes get parked. A build, a linter and fast tests work. A suite that fails until three files exist does not.
- The paths where the checks are defined are protected: a change to one is always parked. For tests the checks find on their own (`go test ./...`), name them with `--protect "**/*_test.go"`.
- Shell commands are parked. A command you can name in advance can be declared: `--away-command "go generate ./..."`. It runs without asking only if it is exactly that command, in the worktree's root, in a sandbox without network. MCP tools are parked unless declared with `--away-tool mcp__<server>__<tool>`. Both are the user's decision made in advance, and a change made that way reaches CAL 2.
- Gemini CLI and OpenCode cannot be given declared commands: they run commands without a sandbox.

## Come back

```bash
staircase decide
```

In a terminal it shows each waiting run as a tree: the change, the checks that ran on exactly that change, and what was parked. The person presses Y to accept (the change is committed on `staircase/run-N` with its certificate), N to reject, D to defer, Z to clarify in a read-only session, or P to prototype a parked change in a checkout that is thrown away.

Without a terminal, decide one run, and only when the user has told you which run and which way:

```bash
staircase decide 12 --accept -m "the user's reason, in their words"
staircase decide 12 --reject -m "the user's reason, in their words"
```

A decision is bound to the review the user saw: add `--shown <entry>` (the entry the list prints) so it is refused if the review changed. `--adopt <n>` adopts parked proposal n into the change, if the checks pass with it. Accepting an empty change delivers nothing.

## How a run stands

`staircase decide <run>` on a run that is not waiting shows its status: one of running, awaiting review, blocked or partial, failed, no change, delivered, or delivered with incomplete evidence, with the reason, its attempts, and the time, tokens and cost it used. For what to do with each, use `investigate-run`.

A run whose agent was lost (the process was killed) is parked until the person says they looked. `staircase acknowledge <run>` records that and launches nothing; then `staircase resume <run>` goes on, `staircase resume <run> --ack-unknown` does both at once, and `staircase recover <run>` commits what had been approved.

## Delivery by policy

`--deliver policy` lets an away run commit to its branch **with no person reviewing the whole change**, but only when seven conditions hold, all read from the run's verified history. Among them: every change was approved by a rule of the user's signed policy, nothing was parked, every path is inside `--deliver-path` and neither sensitive nor protected, and the checks passed on exactly the approved tree. It also needs `--away`, no `--validator`, `--sign-approvals`, a declared `--protect`, and a policy signed with `staircase policy sign`. If any condition fails the run simply waits for review.

Do not turn it on for the user. Describe it, say that nobody reads the change, and let them choose. It suits documentation, changelog entries and generated files, work a rule already decided. See `policy-rules`.
