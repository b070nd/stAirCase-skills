## What it does

`sc:review-and-seal` certifies changes that an agent made outside stAirCase, so only the files you approve are committed. There are two routes. For a cloud agent's pull request, `staircase review` brings the branch's changes in one file at a time. For an agent that edits your own checkout, `staircase attach` and `staircase seal` commit exactly what you staged.

Both routes end at CAL 2: every byte that lands was decided, but nobody governed what the agent did on its own machine. The assistant gives you the commands. You run them, because each file comes to you to approve.

## When to reach for it

Type `/sc:review-and-seal`, or the assistant reaches for it when you have a cloud agent's branch to review, or use Cursor or an IDE assistant in your checkout and want a certificate.

| Your situation | Where to go |
|---|---|
| A cloud agent's pull request or branch | `sc:review-and-seal`, with `staircase review` |
| An agent editing your own checkout | `sc:review-and-seal`, with `staircase attach` and `staircase seal` |
| You can run the agent through stAirCase | [sc:governed-task](governed-task.md), which reaches CAL 3 |

## Common questions

**Can someone bypass the pre-commit hook?**

Yes. `git commit --no-verify` gets through. That is why CI is the second line, with [sc:ci-verify](ci-verify.md).

**Why does my check fail in `review`?**

The check runs in a throwaway checkout of the new commit, which holds tracked files only. A check that needs an ignored directory such as `vendor/` cannot pass there.

## It's working if

- Each changed file came to you to approve or reject.
- Rejected changes are not committed, and for `seal` they stay in your working files.
- The commit carries an `Assisted-by:` trailer, and `staircase verify` accepts it at CAL 2.

## Where it fits

An on-ramp that merges onto the main flow before [sc:ci-verify](ci-verify.md). The map of every skill is [sc:ask](ask.md).
