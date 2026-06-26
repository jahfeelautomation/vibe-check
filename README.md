# Vibe Check

*The senior-engineer and security review your vibe-coded app never got.*

## What it is

Vibe Check is a folder you hand to your own Claude Code. It turns Claude Code
into a senior software engineer plus a security reviewer for a project you built
with an AI coding tool but cannot judge yourself. It reads your actual project,
then gives you an honest Build Review Report: a clear go or no-go, a
plain-English fix list worst first, and an honest list of what it could NOT
check, so you are never fooled into feeling covered when you are not.

## How to run it

Point your Claude Code at this folder and at the project you want reviewed. It
reads the project (it does not interview you, because you came here precisely
because you do not know what to tell it) and returns a Build Review Report. Two
modes:

- **Audit** something you already shipped: review the whole thing.
- **Gate** one new change before you trust it: review the change and what it can
  reach.

## The one rule

It never calls your build secure or ready while anything serious is still open,
and it always shows the full list of what it could NOT check. A small script,
`check.py`, enforces this before any report is shown: a report that overclaims,
or that hides a coverage category, is blocked from reaching you. See
`INVARIANT.md`.

## Run the gate

```
python check.py path/to/report.md     # gate one report (exit 0 pass / 1 fail)
python check.py -                      # read a report from stdin
python check.py --self-test            # prove the gate works (exit 0/1)
```

`--self-test` runs a built-in suite: dishonest reports are blocked, honest ones
(including honest no-go reports) pass. If the suite is green, the gate works.

## Your code stays private

Vibe Check runs inside your own Claude Code, on your machine. Your code never
leaves it, and nothing is stored or sent anywhere. The only thing this public
repository ever reviews is the synthetic, deliberately broken `demo-target/`.
Real reviews happen privately, against your own project.

## What's inside

| File or folder | Its job |
|---|---|
| `brief.md` | The problem, in a real builder's voice. |
| `identity.md` | Who the reviewer is, and how it sounds. |
| `intake.md` | The order it reads your repo in. |
| `rules.md` | The operating loop, the safety stop, and the report format. |
| `INVARIANT.md` | The one rule that is verified by machine. |
| `examples.md` | Four worked examples of findings and verdicts. |
| `check.py` | The blocking gate, with a built-in self-test. |
| `reference/00-coverage-map.md` | The seven lifecycle phases it reviews. |
| `reference/01-could-not-check-manifest.md` | The thirteen things a static read cannot settle. |
| `reference/02-area-checklists.md` | Nine review areas with concrete checks. |
| `demo-target/` | A synthetic vulnerable app, the only thing this repo reviews. |
| `sample-output/` | An honest report that passes the gate, and a tampered one that is blocked. |
| `docs/index.html` | A one-page overview. |

## License

MIT. See `LICENSE`.
