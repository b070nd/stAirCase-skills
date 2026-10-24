# stAirCase skills

Skills for [Claude Code](https://claude.com/claude-code) that make working with [stAirCase](https://github.com/b070nd/stAirCase) quick and safe. stAirCase puts a person's decision between an AI coding agent and a git repository, commits only what was approved, and keeps a signed record that anyone can verify. These skills teach an assistant the workflows around it: how to set a project up, run a task, work while away, certify changes made elsewhere, verify in CI, and find out what happened in a run.

Every skill is named `sc-<name>`, so it can be typed short and does not collide with the commands of other tools. The plugin adds its own namespace on top, as `staircase-skills:sc-<name>`.

## Install

```bash
claude plugin marketplace add b070nd/stAirCase-skills
claude plugin install staircase-skills@staircase
```

Inside a session the same two steps are `/plugin marketplace add b070nd/stAirCase-skills` and `/plugin install staircase-skills@staircase`. The plugin works in every project; the skills only matter where you use stAirCase. Then run `/sc-setup` once in each project, and `/sc-ask` any time you want the map.

## What is in it

Each skill has a page in [docs](docs/sc-ask.md) that says what it does, when to reach for it, and how to tell it is working.

You type these. The assistant never starts them on its own, because each one sets how much a person reads or writes a standing rule.

| Skill | Use it to |
|---|---|
| [`/sc-ask`](skills/sc-ask/SKILL.md) | find the skill or flow that fits your situation |
| [`/sc-setup`](skills/sc-setup/SKILL.md) | record the agent, the CI system and whose repository it is, once per project |
| [`/sc-away-run`](skills/sc-away-run/SKILL.md) | start a task and leave, then decide on what the run left |
| [`/sc-policy-rules`](skills/sc-policy-rules/SKILL.md) | write, test and sign rules that approve some kinds of change automatically |

The assistant reaches for these when a task fits, and you can type them too.

| Skill | Use it to |
|---|---|
| [`sc-basics`](skills/sc-basics/SKILL.md) | learn what stAirCase is and the rules every other skill follows |
| [`sc-onboard-project`](skills/sc-onboard-project/SKILL.md) | set a repository up: checks, scope, protected files, secrets, house rules, without touching the repository |
| [`sc-governed-task`](skills/sc-governed-task/SKILL.md) | have an agent make a change with a person deciding each step, and review the result |
| [`sc-review-and-seal`](skills/sc-review-and-seal/SKILL.md) | certify a cloud agent's pull request, or what an agent changed in your own checkout |
| [`sc-ci-verify`](skills/sc-ci-verify/SKILL.md) | require and check change certificates in CI or on a pull request |
| [`sc-investigate-run`](skills/sc-investigate-run/SKILL.md) | find out what happened in a run, or why one is stuck |
| [`sc-change-set`](skills/sc-change-set/SKILL.md) | tie runs of several repositories into one piece of work and verify them together |

## One rule

The decisions belong to the person. The skills tell an assistant to prepare, explain and inspect, and never to approve, reject or accept on its own judgment. Interactive commands, such as `staircase claude` and `staircase seal`, are handed to you to run in your own terminal. Modes that make a person read less (`--approve-on-evidence`, `--away`, `--deliver policy`) are offered with what they give up, never chosen for you. Nothing of stAirCase goes into a client's repository.

## Which stAirCase release

The skills were checked against one release of stAirCase, named in [`STAIRCASE_VERSION`](STAIRCASE_VERSION). A check runs every `staircase` command and flag the skills and the docs mention against that release's own `--help`, so a typo or a flag that was renamed fails here and not in front of a user. If your `staircase version` is another release, a skill tells the assistant to read `staircase <command> --help` before it trusts a flag.

## Try it

Ask in a project where stAirCase is installed:

- "I want to leave a task running overnight with stAirCase. What do I run?"
- "Set up stAirCase for this repository, and keep it out of the repo." (Type `/sc-setup` for the notes first.)
- "My stAirCase run 12 says blocked. What happened?"

## Develop

```bash
make check      # the tests of the check, and the check of the skills (needs staircase on the PATH)
make validate   # Claude Code's own validator, in strict mode
```

`tools/check_skills.py` fails on:

- a skill whose name is not its folder, or does not start with `sc-`;
- a model-invoked skill whose description does not say when to use it, or a user-invoked skill (`disable-model-invocation: true`) whose description does;
- a skill that `plugin.json` does not list, that the router `sc-ask` does not mention, that this README does not link, or that has no page in `docs`;
- a docs page missing a section, or with the sections out of order;
- a skill named with the wrong form: a user-invoked skill needs the slash (`/sc-away-run`), a model-invoked one must not have it, and a skill may only call a model-invoked one with the Skill tool;
- a broken link, an em dash, an emoji or a hidden character;
- a `staircase` command or flag, in a skill or a docs page, that the installed release does not have.

To add a skill, make `skills/sc-<name>/SKILL.md`, list it in `.claude-plugin/plugin.json`, in the table above and in `sc-ask`, and write `docs/sc-<name>.md`. A skill the assistant may start on its own has a description that begins with what it does and then says "Use when ...". A skill that only you may start has `disable-model-invocation: true` and a one-line description for people. When a new release of stAirCase comes out, change `STAIRCASE_VERSION`, run `make check` and fix what it reports.

## License

MIT, see [LICENSE](LICENSE).
