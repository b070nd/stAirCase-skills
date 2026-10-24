---
name: setup
description: Set up this project for the stAirCase skills: record the agent, the CI system and whose repository it is, in a short block of notes. Run once per project.
disable-model-invocation: true
---

# Set up the stAirCase skills

Write the short block of notes that the other skills read, and check the machine. This is a conversation, not a script: look, say what you found, confirm, then write.

Call the Skill tool with "sc:basics" first, unless it was loaded earlier in this conversation.

## 1. Look

- `staircase version` and `staircase doctor`: is stAirCase installed, and which agents are installed and logged in? The skills were checked against the release in this plugin's `STAIRCASE_VERSION`. If the installed one differs, say so.
- `git remote -v`: which host does the repository live on?
- `CLAUDE.md`, `AGENTS.md` and `CLAUDE.local.md` at the repository root: which exist, and is there already a `## stAirCase` block?
- `.github/workflows/` or `.gitlab-ci.yml`: which CI system runs here?
- `staircase vendor list`: is there a vendor for this project yet?

## 2. Ask

One question at a time. Lead with what you found as the recommended answer, so it can be accepted in a word.

1. **Whose repository is it?** Mine, or a client's or employer's. This decides where the notes go, so ask even when the remote looks obvious.
2. **Which agent do you run most?** `claude`, `codex`, `gemini` or `opencode`, from what `staircase doctor` showed as installed. All four are experimental adapters.
3. **Where does CI run?** GitHub Actions, GitLab, or none yet.

Do not ask about approval modes. The block says that `--approve-in-scope`, `--approve-on-evidence`, `--away` and `--deliver policy` are never chosen for the person.

## 3. Show the draft and let them edit it

```markdown
## stAirCase

Agent runs here are governed by stAirCase. The decisions belong to the person: prepare, explain and inspect, and never approve, reject or accept for them. Start with the skill sc:basics.

- Agent: claude
- CI: GitHub Actions
- Modes that make a person read less (--approve-in-scope, --approve-on-evidence, --away, --deliver policy) are offered, never chosen for them.
```

Fill the two values from the answers.

## 4. Write it

| Whose repository | Where the block goes |
|---|---|
| Mine | `CLAUDE.md` if it exists, else `AGENTS.md` if it exists. If neither exists, ask which to create. Never create one when the other is there. Update an existing `## stAirCase` block in place. |
| A client's or employer's | `CLAUDE.local.md`, which is read next to `CLAUDE.md` and is yours alone. Add the line `CLAUDE.local.md` to `.git/info/exclude`, not to `.gitignore`, so no tracked file changes. Nothing of stAirCase goes into the repository. |

Say which file you wrote and that nothing else was changed.

## 5. Next

The project profile: call the Skill tool with "sc:onboard-project". To see every skill and how they fit, the user can run `/sc:ask`.
