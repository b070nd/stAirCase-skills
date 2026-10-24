## What it does

`sc:change-set` ties the runs of several repositories into one piece of work. A change across a backend, a middleware and a frontend is several runs, one per repository, each with its own worktree and certificate. A change set is an id that ties them together, plus one command that checks all of them.

It also handles contracts: a file shared between repositories, such as an API description. When one member changes a contract, every other member must acknowledge that exact content before the set verifies.

## When to reach for it

Type `/sc:change-set`, or the assistant reaches for it when a change spans repositories of one product, or when files are contracts between repositories.

| Your situation | Where to go |
|---|---|
| One change across several repositories | `sc:change-set` |
| One repository | [sc:governed-task](governed-task.md) |

## Prerequisites

Each repository onboarded with [sc:onboard-project](onboard-project.md). Contracts should be sensitive paths, so an agent never changes one without a person.

## It's working if

- The set exists before the first run, and each run was started with its id.
- `staircase changeset show` lists one run per project and the contracts.
- `staircase changeset verify` names the member, or the contract, that fails, and exits non-zero until the whole set is accepted.

## Where it fits

An on-ramp to the main flow, used instead of one [sc:governed-task](governed-task.md) for several repositories, then checked by [sc:ci-verify](ci-verify.md). The map of every skill is [sc:ask](ask.md).
