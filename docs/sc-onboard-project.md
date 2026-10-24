## What it does

`sc-onboard-project` makes the project profile: what is true of the repository for every run. The checks, the files that define them, the paths that always need a person, where a task may change files, which ignored directories the checks need, which tracked files hold secrets, and the house rules every agent is told.

It proposes a value for each row from the repository and lets you correct it. The profile lives in the stAirCase workspace and never in the repository, so it works the same for your own project and for a client's.

## When to reach for it

Type `/sc-onboard-project`, or the assistant reaches for it when you want to start using stAirCase on a project, protect test files, or keep secrets away from agents. Reach for it before the first run on any project that has tests or secrets.

| Your situation | Where to go |
|---|---|
| A project with tests, contracts or secrets, not yet set up | `sc-onboard-project` |
| The notes about your agent and CI | [sc-setup](sc-setup.md) |
| You already have a profile and want to run a task | [sc-governed-task](sc-governed-task.md) |

## Common questions

**Why protect the test files?**

A check is only evidence if the agent cannot edit what it runs. Tests that nothing protects can be weakened to pass.

**Can an instruction in the profile keep an agent out of a file?**

No. Instructions are words to a model, not enforcement. What must hold belongs in `--protect`, `--sensitive` and `--scope`, where a person decides.

## It's working if

- Every row of the profile was proposed, and you corrected or accepted each one.
- `staircase project profile show` lists what you decided, and `git status` in the repository shows no change.
- After the first run, `staircase case briefing` prints what the agent was told, house rules included.

## Where it fits

A chain step after [sc-setup](sc-setup.md) and before [sc-governed-task](sc-governed-task.md). For one product spread over several repositories, onboard each, then use [sc-change-set](sc-change-set.md). The map of every skill is [sc-ask](sc-ask.md).
