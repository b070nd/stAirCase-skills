---
name: policy-rules
description: Write, test and sign the stAirCase policy.json so some kinds of change are approved or rejected automatically. Use when the user wants rules that approve small or safe changes without asking, wants to reject changes from an agent or to a path, asks what a policy rule can and cannot decide, wants to test a policy against past runs, or hits a policy load or integrity error.
---

# Policy rules

A policy is `policy.json` in the workspace (`~/.staircase-workspace/policy.json` by default). Rules are checked in order and the first that matches decides. A proposal no rule matches goes on to the validator models or to a person. Rules approve or reject; they never read a change, they match what stAirCase derived from it.

## What a rule can and cannot do

- Shell commands and tool calls are **never** approved by a rule. The one exception is a command the user declared for an away run (`away-run`).
- Changes to the paths where checks are defined (protected) and to sensitive paths (CI and build files, dependency files, `.env` files, shell scripts, `CODEOWNERS`) always go to a person, whatever a rule says. A rule cannot widen that, and a `reject` rule does not catch them first: they are parked or asked.
- A rule that matches is the user's decision made in advance, so write each one narrowly and say what it will approve.

## Write it with the user

```json
{
  "version": 1,
  "rules": [
    { "action_types": ["file_edit"], "paths": ["docs/**"], "max_lines": 40, "no_deletions": true, "effect": "approve" },
    { "agent_names": ["intern"], "effect": "reject" }
  ],
  "limits": { "max_auto_approved": 20, "max_total_yields": 50 }
}
```

All fields of a rule must match. The fields: `action_types`, `allowed_extensions`, `agent_names`, `min_confidence`, and the conditions on the change itself: `paths` (every changed file matches one glob, in any letter case), `max_lines`, `max_files`, `new_files_only`, `no_deletions`; and `effect`, `approve` or `reject`. `limits` send every later proposal to a person once reached.

The file is strict: it must parse, an unknown field stops the run, and a reject rule with no conditions at all is refused unless `"allow_blanket_deny": true`. An older stAirCase refuses a file that uses the change conditions: that is on purpose.

## Test before use

```bash
staircase policy test new-policy.json
```

It replays every proposal recorded in the workspace against the file and shows what would be decided differently. Read first the section about changes **a person rejected that the policy would approve**: each one is a rule that is too wide. It also lists past decisions that a protected or sensitive path would now send to a person. Line counts and new files are estimates in the replay.

## Sign it

```bash
staircase policy sign
staircase policy verify
```

A signed policy is checked when a run starts: a file changed after signing stops the run (`policy integrity check failed`; if the user made the change, sign again). Delivery by policy needs a signed policy (`away-run`).

## What to tell the user

A rule is only as safe as the checks behind it. Rules suit work whose correctness a rule really decides: documentation, changelog entries, generated or formatted files, the areas `paths` names. Code that only passed its checks is better left to `--approve-on-evidence` or to a person.
