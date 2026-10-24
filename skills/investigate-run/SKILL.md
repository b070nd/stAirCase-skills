---
name: investigate-run
description: Find out what happened in a stAirCase run, or why one is stuck, failed, halted or looks wrong. Use when a run ended FAILED, shows blocked or partial, was halted for drift, was interrupted or killed, left a worktree with unapproved changes, says the audit chain is broken, or the user asks what was decided and by whom. Also for staircase doctor warnings.
---

# Investigate a run

Call the Skill tool with "sc:basics" first, unless it was loaded earlier in this conversation: it holds the rules every stAirCase skill follows.

Everything here reads. You look, explain, and give the user the command to run. You never repair a run's records.

## Look

```bash
staircase doctor
staircase inspect runs
staircase inspect log 12
staircase decide 12
staircase replay 12
```

- `doctor` checks the workspace and lists runs that were interrupted holding approved changes.
- `inspect runs` lists runs with their outcome (`--case <id>` narrows it). `inspect log <run>` prints the audit chain entry by entry and **verifies it**: each entry is marked `ok` or `TAMPERED`, and the end says whether the hash chain is intact. Add `--full` for complete payloads.
- `decide <run>` shows a run that is not waiting: its outcome, why, attempts, and the time, tokens and cost used against its limits.
- `replay <run>` prints the approval decisions of a finished run, after verifying its chain.

Redact secrets before you show any of it.

## Read the outcome

| Outcome | What to do |
|---|---|
| running | its process holds the run. Wait, or ask the user whether it is still alive |
| awaiting review | the person decides: `staircase decide <run>` (the user can run `/sc:away-run` to be walked through it) |
| blocked or partial | read the reason; the next table has the usual ones |
| failed | `inspect log` shows which checks failed, which review was rejected, or which file differed |
| no change | nothing was approved or parked and the checks pass on the unchanged tree: nothing to deliver |
| delivered | the commit is on `staircase/run-N` with its evidence |
| delivered with incomplete evidence | the commit is there, but the ledger, certificate or a note could not be written; the log has an `evidence_failed` entry |

## Stuck runs

| What it says | What to do |
|---|---|
| the agent's last launch has no known end (killed, crashed) | look at what the agent may have done, then the person runs `staircase acknowledge <run>`, then `staircase resume <run>`; or `staircase resume <run> --ack-unknown` for both; or `staircase recover <run>` to commit what was approved. Three lost launches are never resumed: recover |
| halted for drift | read `staircase inspect log <run>`, then the person continues with `--ack-drift` |
| the worktree holds changes nobody approved | look at them; `staircase resume <run> --discard-unapproved` puts it back to the approved state |
| no agent session to pick up | `staircase resume <run> --fresh-context` continues in a new session grounded by the audit chain |
| time limit used up, or the run saved no options | `staircase recover <run>` is the only way |
| the run branch is not at the run's base | the branch moved or was deleted; `recover` reports what it can |
| `approval_content_mismatch`, `unapproved_worktree_change`, `run_branch_moved` | the safety check worked and nothing was committed; the failed run's worktree is kept in the workspace for the user to look at |

`resume` continues the same run under the policy and options it saved. `recover` does not run the agent, it commits exactly what was approved. Neither changes anything unless every check passes.

## If the chain is broken

`TAMPERED` on an entry, or a chain that does not verify, means a record was changed after it was written. Stop. Do not edit, delete or "fix" anything in the workspace. Tell the user, keep a copy of the workspace folder, and let them decide. `staircase audit export <run>` and `staircase audit verify <checkpoint>` check a signed copy of the record from another place.

## Still stuck

Run again with `--debug` (for `staircase run`) to write every agent message to the workspace's `log/` folder. The documentation's troubleshooting page lists the error messages: https://github.com/b070nd/stAirCase/blob/master/docs/troubleshooting.md. Strip keys and private code before the user posts anything in an issue.
