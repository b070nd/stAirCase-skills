## What it does

`sc-investigate-run` finds out what happened in a run, or why one is stuck, failed, halted or looks wrong. It reads the audit chain, which is verified as it is read, explains the outcome, and gives you the command that continues or recovers the run.

It only reads. It never repairs a run's records. When an entry is marked `TAMPERED`, it stops and tells you, because a record was changed after it was written.

## When to reach for it

Type `/sc-investigate-run`, or the assistant reaches for it when a run ended failed, shows blocked or partial, was halted for drift, was killed, left a worktree with unapproved changes, or when `staircase doctor` warns.

| Your situation | Where to go |
|---|---|
| A run ended or stuck in a way you do not understand | `sc-investigate-run` |
| A run is waiting for your decision | [sc-away-run](sc-away-run.md) |
| You want to start a new task | [sc-governed-task](sc-governed-task.md) |

## It's working if

- It starts with `staircase doctor` and `staircase inspect`, and shows you the outcome before it suggests anything.
- Each fix it names is a command for you to run, with the reason.
- Secrets in anything it shows are written `<REDACTED>`.
- On a broken chain it touches nothing and tells you to keep a copy of the workspace.

## Where it fits

Standalone: reach for it any time after a run. It leads back to [sc-governed-task](sc-governed-task.md) or [sc-away-run](sc-away-run.md) once the run is dealt with. The map of every skill is [sc-ask](sc-ask.md).
