---
name: sc-change-set
description: Tie runs of several repositories into one piece of work and verify them together. Use when a change spans a backend, a middleware and a frontend, or any repositories of one product, when files are contracts between repositories (an API description, a schema) that need acknowledging, or when the user asks for a change set.
---

# Change sets

Call the Skill tool with "sc-basics" first, unless it was loaded earlier in this conversation: it holds the rules every stAirCase skill follows.

A change across several repositories is several runs, one per repository. Each run stays what it always is: one repository, its own worktree, chain and certificate. A **change set** is an id that ties them together, plus one command that checks all of them. The set is a file in the workspace, never in a repository.

## 1. Make the set, before the runs

The id is chosen by the user (lower case letters, digits, `.`, `-`, `_`), so a run can name it before it exists.

```bash
staircase changeset create checkout-v2
```

## 2. Start each run with the id

The user runs one governed task per repository, in that repository (`sc-governed-task`):

```bash
staircase claude --change-set checkout-v2 "add the order endpoint"
```

The id goes on the run's record and on its certificate (the optional `changeSet` field, which older verifiers ignore). A set that does not exist is refused.

## 3. Add the runs, name the contracts

```bash
staircase changeset add checkout-v2 12 13 14
staircase changeset contract checkout-v2 backend:api/openapi.yaml
staircase changeset show checkout-v2
```

A set has one run per project: adding another run of the same project replaces the first. A project is named by its id or its name. A contract is a literal file path from its repository's root. Make the contract's path sensitive in the project's profile so an agent can never change it without a person (`staircase project profile set <id> --sensitive <path>`); `changeset contract` says when it is not.

## 4. Acknowledge contract changes

When a member's run changed a contract in its own project, every other member must acknowledge that exact content. The person looks at the change, then:

```bash
staircase changeset ack checkout-v2 backend:api/openapi.yaml --by frontend
```

The acknowledgement is bound to the content: a later change to the file needs a new one. A project cannot acknowledge its own change, and the command is refused if the run did not change the file. It is a record in the workspace file, not a signature: it says who looked and under which git email, which is not proof.

## 5. Verify the whole set

```bash
staircase changeset verify checkout-v2 --min-cal 3
```

For every member it checks that the run was delivered (by its own verified history), that its certificate verifies against the workspace key, is about the run's commit, reaches the level asked, records no failed check and names this set, and that every contract change in the member's project is acknowledged by every other member. A failure names the member, or names the contract, the project that changed it and the project that has not accepted it. The command exits non-zero: accept the whole set or nothing.

## Limits to tell the user

- Verification uses the signing key of the workspace that made the runs. Verifying on another machine with other keys is not built.
- One agent does not work in several repositories in one session: a person, or an orchestrating agent, starts one run per repository.
- A set does not order the runs. Dependencies between projects and the dependency gate do that.
