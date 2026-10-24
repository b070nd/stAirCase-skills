---
name: ci-verify
description: Require or check stAirCase change certificates in CI or on a pull request. Use when the user wants a required check that refuses commits an AI agent helped make without a valid certificate, sets up the GitHub Action or a GitLab job, wants to verify a commit or a range locally, asks what a CAL level means, or hits a failure of staircase verify.
---

# Verify in CI

Call the Skill tool with "sc:basics" first, unless it was loaded earlier in this conversation: it holds the rules every stAirCase skill follows.

Every commit a governed run makes carries a **change certificate** (a signed statement of who helped, what was decided, and the assurance level) as a git note. Verifying checks that the certificate is valid, is about exactly that commit, reaches the level asked, and records no failed check.

## The levels

| Level | Means |
|---|---|
| CAL 1 | attributed: the commit says which agents took part, nothing is enforced |
| CAL 2 | reviewed: every byte an agent wrote was covered by a recorded decision, and the commit can be rebuilt |
| CAL 3 | gated: every action was decided before it ran, in an isolated worktree, no approved command outside a sandbox |
| CAL 4 | two-party: a CAL 3 change signed by a trusted reviewer who did not start the run |

`--min-cal` fails below the level you name. A check requires a level, it never raises one.

## Check locally first

```bash
staircase verify staircase/run-7
staircase verify main..HEAD --all --min-cal 3 --rebuild
```

`--all` requires a certificate on every commit of the range. Without it only commits that name an agent in an `Assisted-by:` trailer are checked, which an agent commit can dodge by leaving the trailer out. `--rebuild` replays each commit from its ledger and requires the same tree: a validly signed certificate on a commit that holds other bytes fails.

## The trust comes from a protected ref, never from the change

The public key (the workspace's `.signing.pub`, safe to commit) must be read from a branch the change under test cannot alter. `verify` can do that itself, on any CI system, and refuses a ref that is, or holds, a commit being verified:

```bash
staircase verify origin/main..HEAD --all --min-cal 2 --rebuild --trust-ref origin/main --key-path .github/staircase.pub
```

For CAL 4 add `--signers-path .github/allowed_signers` and `--require-initiator`.

## GitHub

Commit the public key to the protected branch, push the certificates with the branch, and add a workflow:

```yaml
name: stAirCase
on: pull_request
permissions:
  contents: read
  attestations: read
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0
      - uses: b070nd/stAirCase@<release tag you have verified>
        with:
          version: <the same release tag>
          key: .github/staircase.pub
          min-cal: 3
          rebuild: true
```

```bash
git push origin staircase/run-7 refs/notes/staircase refs/notes/staircase-ledger
```

Pin the action to a release tag. The action verifies how the release was built before it runs it. Make the check a required status check, and protect the key path with CODEOWNERS and a ruleset that requires review: a check that the change under test can edit or skip is not a gate. If your bases differ in what they require, give each its own job name and require only that base's name in that base's ruleset.

## GitLab and others

The check is one command over a range. For a merge request job, end the range at `CI_MERGE_REQUEST_SOURCE_BRANCH_SHA`, not at `CI_COMMIT_SHA`: in a merged-results pipeline the second is a commit GitLab made, which has no certificate. Fetch the notes, then run the command above with `--trust-ref "origin/$CI_MERGE_REQUEST_TARGET_BRANCH_NAME"`. The documentation has a job to start from; it has not been run on a GitLab instance, so try it on a test project first.

## Limits to tell the user

- A certificate is about one commit id. Squash-merge and rebase-merge make new commits with no certificate: check the pull request's own commits before merging, merge with a merge commit, or certify the merged result with `staircase seal`.
- A pull request from a fork has no notes in the repository and fails closed.
- Notes are ordinary refs: restrict who may push `refs/notes/staircase*`.
- A CAL 4 requester is by default the git email of the checkout, which anyone can set. `--require-initiator` counts CAL 4 only when the person who started the run signed the request with a trusted key.
