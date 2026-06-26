# The one rule we verify by machine

## Why one rule is mechanical

Most of this folder is judgment written in prose: how to read a project, how to
weigh a finding, how to phrase a verdict. Judgment cannot be checked by a
machine, and a reviewer cannot prove to you that it exercised good judgment.
There is one thing that can be made mechanical, and it is the thing that matters
most to someone who cannot grade the work themselves: the report must never lie
about how covered you are. So that single promise is named here and enforced by
a small program that blocks the report from being shown if the promise is
broken.

## The invariant

> The Build Review Report never calls the build secure or ready while any
> serious issue is unresolved or any required coverage category is hidden. It
> always discloses its full declared coverage: every could-not-check item
> (CNC-01..CNC-13) and all seven lifecycle phases (PHASE-1..PHASE-7).

A "serious issue" is a finding labeled CRITICAL, HIGH, or COULD-NOT-VERIFY that
has not been marked resolved. While one of those is open, the report cannot
carry a go-ahead verdict or any sentence claiming the build is secure or ready.

## The blocking check

The rule is enforced by `check.py` (Python standard library only, no network,
no dependencies):

```
python check.py path/to/report.md     # gate one report (exit 0 pass / 1 fail)
python check.py -                      # read report from stdin
python check.py --self-test            # run the regression suite (exit 0/1)
```

Exit code 0 means the report is honest and complete about its coverage and may
be shown. Exit code 1 means it may not. `rules.md` makes running this gate the
mandatory final step before any report reaches you: a draft that fails the gate
is never delivered.

## What it catches, and what it honestly cannot

Two honest limits, stated plainly so you are never misled about the guarantee:

1. **It is a canonical floor on verdict phrasing, not every possible wording.**
   The gate catches the common shapes of an overclaim (a go-ahead verdict, or
   sentences like "this build is secure" or "safe to ship") while a serious
   finding is open. A determined paraphrase could slip past the regex. The
   discipline in `rules.md` carries the rest; the gate is the floor, not the
   ceiling.

2. **It verifies that DISCLOSURE is complete, never that the FINDINGS are
   complete.** No automated review, this one included, can promise it found
   every bug. What Vibe Check can promise, and does enforce, is that everything
   it could not verify from a static read is disclosed in full: all thirteen
   could-not-check items and all seven lifecycle phases appear in every report.
   You are never told a category was covered when it was not.

## Why this file exists

The honest discriminator for a tool like this is not "trust my judgment." It is
"here is the one thing I verify deterministically, and here is the program that
verifies it." Everything else in this folder is craft. This is the load-bearing
promise, and it is the one you can check yourself by running the gate.
