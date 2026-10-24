---
name: onboard-project
description: Set stAirCase up for a repository, your own or a client's, so every run on it uses the right checks, scope and protections without putting anything into the repository. Use when the user wants to start using stAirCase on a project, set what a run may touch or must check, protect test files or contract files, keep secrets away from agents, keep stAirCase out of a client's repo, or fix a project's profile.
---

# Onboard a project

Call the Skill tool with "sc:basics" first, unless it was loaded earlier in this conversation: it holds the rules every stAirCase skill follows.

The goal is a **project profile** in the workspace that holds what is true of the repository for every run. Nothing is written into the repository.

## 1. Check the machine

```bash
staircase version
staircase doctor
```

Read each row. `ok` is fine. `warn` is information: a tool is missing or an agent is not logged in, fix only what the user needs. `FAIL` comes first: the message says how to fix it. With no workspace yet, `staircase init` creates it.

## 2. Make the project

`staircase claude "<task>"` creates the workspace, the project and the case when they are missing, so a first try needs nothing else. To set the profile before the first run, create the project yourself. Ask the user for the vendor name (a namespace, such as the client or team) and the repository's absolute path.

```bash
staircase vendor add acme
staircase project add acme shop --source /absolute/path/to/shop
staircase project list acme
```

The id that `project list` shows (#1 for the first) is the id in the commands below.

## 3. Decide the profile with the user

Look at the repository, propose a value for each row, and let the user correct it. Do not guess in silence.

| Question | Field | Example |
|---|---|---|
| What command runs the tests? | `--check` | `"go test ./..."` |
| Which files define those tests, so an agent cannot weaken them? | `--protect` | `"**/*_test.go"`, `phpunit.xml` |
| Which files must always need a person, such as contracts and schemas? | `--sensitive` | `api/openapi.yaml` |
| Where may a task change files? | `--scope` | `"src/**"` |
| Which ignored directories do the checks need? | `--visible` | `vendor` |
| Which tracked files hold secrets the agent must not read? | `--unreadable`, or `--unreadable-defaults` | `auth.json` |
| What house rules should every agent be told? | `--instructions` or `--instructions-file` | the copyright header, "patches only" |

CI and build files, dependency files, `.env` files, shell scripts and `CODEOWNERS` files always need a person already. A check is only evidence if the agent cannot edit what it runs: tests that nothing protects can be weakened.

```bash
staircase project profile set 1 --check "go test ./..." --protect "**/*_test.go" --scope "src/**"
staircase project profile show 1
```

A field you name replaces its old value, `--clear <field>` removes one, and paths are written from the repository's root. A profile can add paths that need a person and never take any away. A flag on a run overrides the profile for that run.

## 4. Say these things to the user

- Instructions are words to a model, not enforcement. What must hold belongs in `--protect`, `--sensitive` and `--scope`, where a person decides.
- Unreadable paths are enforced for the built-in agent and Claude Code. Codex, Gemini CLI and OpenCode cannot be held to them, so a run with those on such a project is refused, and the message names the agent.
- `--visible` shows an ignored directory to the checks read-only. It is never in the agent's worktree and never part of what is approved.
- The profile is a file in the workspace, not signed, and a profile that cannot be read stops the run.

## 5. Check it

After the first run, `staircase case briefing <case-id>` prints exactly what an agent is told, instructions included.

## Next

`sc:governed-task` for the first run. For several repositories of one product, `sc:change-set`.
