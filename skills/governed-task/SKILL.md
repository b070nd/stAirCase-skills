---
name: governed-task
description: Have an AI coding agent make a change in a repository with stAirCase deciding every step. Use when the user wants to run Claude Code, Codex, Gemini CLI or OpenCode on a task under stAirCase, choose how much to approve by hand, set the scope and checks of a task, review the branch a run produced, throw a run away, or continue a run that was interrupted.
---

# A governed task

Call the Skill tool with "sc:basics" first, unless it was loaded earlier in this conversation: it holds the rules every stAirCase skill follows.

The person starts the run in their own terminal and approves in it. You prepare the command, explain what will happen, and check the result afterwards.

## 1. Before

- The repository needs at least one commit. The agent works on the **last commit**: uncommitted work is not in its copy, and neither are ignored paths such as `vendor/`. stAirCase warns and names the files. Ask the user to commit first if the agent should see them.
- If the repository has checks, protected files or secrets, set the project up first (`sc:onboard-project`).
- Pick the agent: `staircase claude`, `codex`, `gemini` or `opencode`. All four are experimental adapters. `staircase doctor` shows which are installed and logged in.

## 2. Choose how much the person decides

| Mode | Flags | The person still decides | What it gives up |
|---|---|---|---|
| Every change | none | every file change, every command | nothing |
| In-scope as part of the task | `--allow` and `--approve-in-scope` | anything outside the scope, sensitive files, guard hits, commands, 1 in 5 of the rest, and the whole change at the end | in-scope changes are read less |
| On evidence | `--allow`, `--check` and `--approve-on-evidence` | the same, plus any change where the checks fail or are missing | trusts the checks to be strong |

Shell commands are off. `--allow-shell-exec` lets the agent ask, and each command still needs approval. Say plainly that evidence is only as good as the checks, and that `--protect` stops the agent editing them.

## 3. The command

Give the user this to run in their terminal, with their task, scope and check:

```bash
staircase claude "add a /health endpoint that returns 200" --allow "src/**" --check "go test ./..."
```

What they will see: first a summary (the task, where files may change, how edits and commands are handled, the model, the budget). `y` and Enter start it. Then each change shows the exact bytes it would produce: `y` approves, `n` rejects, and the reason goes back to the agent.

## 4. After

At the end the approved changes are on `staircase/run-N` and the user's checkout is untouched. You may look:

```bash
git diff HEAD...staircase/run-N
git log --stat -1 staircase/run-N
staircase verify staircase/run-N
```

A commit does not say a story is done: the person does. The run prints the exact `staircase story accept <id>` command. Then they merge the branch the usual way, or `staircase push` pushes it and opens a pull request. To throw a run away, `staircase case rollback <case-id>` removes its branch and worktree and keeps the audit record.

If the run ended `FAILED` with `approval_content_mismatch`, `unapproved_worktree_change` or `run_branch_moved`, the safety check worked: nothing was committed. `sc:investigate-run` explains.

## 5. If it was interrupted

`staircase resume <run>` carries on with the same task. `staircase recover <run>` does not run the agent: it commits exactly what had been approved. When `resume` refuses it says why and changes nothing; `sc:investigate-run` has the table.
