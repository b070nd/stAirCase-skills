## What it does

`sc:ci-verify` sets up and explains the check that refuses commits an AI agent helped make without a valid change certificate. A certificate is a signed statement of who helped, what was decided and the assurance level. Verifying checks that it is valid, is about exactly that commit, reaches the level asked, and records no failed check.

The trust comes from a protected ref. The public key is read from a branch the change under test cannot alter, so a change cannot edit the check that judges it.

## When to reach for it

Type `/sc:ci-verify`, or the assistant reaches for it when you want a required check, the GitHub Action or a GitLab job, a local verification of a commit or range, an explanation of a CAL level, or help with a failed `staircase verify`.

## Prerequisites

Certificates exist only on commits that a run made or that `staircase seal` made. Push the notes with the branch (`refs/notes/staircase` and `refs/notes/staircase-ledger`).

## Common questions

**Why does a squash merge fail the check?**

A certificate is about one commit id, and squash and rebase merges make new commits with no certificate. Check the pull request's own commits before merging, merge with a merge commit, or certify the merged result with `staircase seal`.

**Why does a pull request from a fork fail?**

A fork has no notes in the repository, so it fails closed.

**Is the GitLab job tested?**

Not yet on a GitLab instance. Try it on a test project first.

## It's working if

- `staircase verify` passes locally on a range before CI is set up.
- The key is read with `--trust-ref` from a protected branch, and the key path is protected by CODEOWNERS and a review rule.
- The check is a required status check, and the action is pinned to a release tag.

## Where it fits

The last step of the main flow, after the merge. [sc:review-and-seal](review-and-seal.md) feeds it commits from agents that run outside stAirCase. The map of every skill is [sc:ask](ask.md).
