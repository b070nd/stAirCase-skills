# stAirCase skills

Skills for [Claude Code](https://claude.com/claude-code) that make working with [stAirCase](https://github.com/b070nd/stAirCase) quick and safe. stAirCase puts a person's decision between an AI coding agent and a git repository, commits only what was approved, and keeps a signed record that anyone can verify. These skills teach an assistant the workflows around it: how to set a project up, run a task, work while away, certify changes made elsewhere, verify in CI, and find out what happened in a run.

## Install

```bash
claude plugin marketplace add b070nd/stAirCase-skills
claude plugin install staircase-skills@staircase
```

Inside a session the same two steps are `/plugin marketplace add b070nd/stAirCase-skills` and `/plugin install staircase-skills@staircase`. The plugin works in every project; the skills only matter where you use stAirCase.

## What is in it

| Skill | Use it to |
|---|---|
| [`staircase`](skills/staircase/SKILL.md) | get oriented, and learn the rules every other skill follows |
| [`onboard-project`](skills/onboard-project/SKILL.md) | set a repository up: checks, scope, protected files, secrets, house rules, without touching the repository |
| [`governed-task`](skills/governed-task/SKILL.md) | have an agent make a change with a person deciding each step, and review the result |
| [`away-run`](skills/away-run/SKILL.md) | start a task and leave, then decide on what the run left, or recover a lost run |
| [`review-and-seal`](skills/review-and-seal/SKILL.md) | certify a cloud agent's pull request, or what an agent changed in your own checkout |
| [`ci-verify`](skills/ci-verify/SKILL.md) | require and check change certificates in CI or on a pull request |
| [`investigate-run`](skills/investigate-run/SKILL.md) | find out what happened in a run, or why one is stuck |
| [`change-set`](skills/change-set/SKILL.md) | tie runs of several repositories into one piece of work and verify them together |
| [`policy-rules`](skills/policy-rules/SKILL.md) | write, test and sign rules that approve some kinds of change automatically |

## One rule

The decisions belong to the person. The skills tell an assistant to prepare, explain and inspect, and never to approve, reject or accept on its own judgment. Interactive commands, such as `staircase claude` and `staircase seal`, are handed to you to run in your own terminal. Modes that make a person read less (`--approve-on-evidence`, `--away`, `--deliver policy`) are offered with what they give up, never chosen for you.

## Which stAirCase release

The skills were checked against one release of stAirCase, named in [`STAIRCASE_VERSION`](STAIRCASE_VERSION). A check runs every `staircase` command and flag the skills mention against that release's own `--help`, so a typo or a flag that was renamed fails here and not in front of a user. If your `staircase version` is another release, a skill tells the assistant to read `staircase <command> --help` before it trusts a flag.

## Try it

Ask in a project where stAirCase is installed:

- "I want to leave a task running overnight with stAirCase. What do I run?"
- "Set up stAirCase for this repository, and keep it out of the repo."
- "My stAirCase run 12 says blocked. What happened?"

## Develop

```bash
make check      # the tests of the check, and the check of the skills (needs staircase on the PATH)
make validate   # Claude Code's own validator, in strict mode
```

`tools/check_skills.py` fails on a skill whose name is not its folder, whose description does not say when to use it, that `plugin.json` does not list, that has a broken link, an em dash, an emoji or a hidden character, or that shows a `staircase` command or flag the installed release does not have. To add a skill, make `skills/<name>/SKILL.md`, list it in `.claude-plugin/plugin.json` and in the table above. When a new release of stAirCase comes out, change `STAIRCASE_VERSION`, run `make check` and fix what it reports.

## License

MIT, see [LICENSE](LICENSE).
