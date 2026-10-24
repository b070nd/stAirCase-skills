## What it does

`sc:basics` says what stAirCase is, in a paragraph, and holds the rules every other skill follows. The rule behind all of them is that the decisions belong to the person: the assistant prepares, explains and inspects, and never approves, rejects or accepts on its own judgment.

The other rules follow from it. Interactive commands, such as `staircase claude` and `staircase seal`, are handed to you to run in your own terminal. Modes that make a person read less are offered with what they give up, never chosen. A secret never goes on a command line. Nothing of stAirCase goes into a client's repository. A broken audit chain is never repaired.

## When to reach for it

The assistant reaches for it when the conversation mentions stAirCase, and the other model-invoked skills load it first. You can also type `/sc:basics`. Reach for it yourself when you want the rules stated, or when an assistant seems to be deciding for you.

## It's working if

- The assistant gives you the command to run for `staircase claude`, `seal` and `review`, and does not run them.
- It does not add `-y`, and does not answer a prompt for you.
- It asks before it suggests `--approve-in-scope`, `--approve-on-evidence`, `--away` or `--deliver policy`, and says what each gives up.
- Secrets in anything it shows you are written `<REDACTED>`.

## Where it fits

It sits underneath the other skills and is never a step of a flow. Each of them calls for it at its start. The map of every skill is [sc:ask](ask.md).
