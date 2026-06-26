# Case study 2: an automation that writes into an outside system of record

Case study 1 was a wide pass over a whole shipped app. This one goes the other
way: a second real run that deep-dives the single most dangerous kind of thing
software can do, on another of our own production apps. Same Vibe Check folder,
audit mode. Everything below is from a real run, sanitized. No product name, no
client name, no file paths, no library names, no code, no secrets. Category level
only.

The dangerous thing is this: a piece of the app drives an outside web system of
record, the kind a person normally fills in by hand, and types real business data
into it. At the end of that process there is a final commit that cannot be undone.
In plain terms, the software fills out the form, and the last "submit" is the
button you can never un-press.

So the one question that matters is blunt. Can the machine press that button by
mistake? If it can, nothing else about the feature is safe. This run was about
answering that, in the code, and then drawing an honest line around what reading
the code cannot settle.

## How it was run

Same folder, audit mode. A Claude Code session was pointed at the Vibe Check
folder and the real subsystem. It read the code; it never ran the app. One pass
over the parts that matter for an irreversible write: the planner that decides
what gets typed where, the executor that actually drives the outside system, and
the tests that are supposed to keep the safety promise from drifting.

## What it confirmed (the safety boundary held)

The answer to the blunt question is no, the machine cannot press the final button,
and it is locked that way three independent times. Any one of these alone would
stop an accidental submit. All three are present at once:

- The list of actions the planner is even allowed to describe has no "submit" in
  it. The machine has no word for the irreversible step, so a plan literally
  cannot contain one. For the last page, the plan ends on an explicit "stop here,
  a human takes it from here" marker instead.
- The part that actually drives the outside system has no submit-shaped command on
  it at all. The strongest thing it can do is a save, not the final commit. When the
  run reaches the stop marker, it halts and does nothing more.
- There is a test that fails the build if anyone ever adds a submit command to
  that driver. So the protection is not a comment or a habit a future change could
  quietly erase. If someone tries to wire up an auto-submit, the project stops
  compiling.

Two more things a senior reviewer checks on this kind of feature, both clean:

- The run is fail-safe. If a field is missing the information it needs, the machine
  skips it and reports it rather than guessing. If the outside system does
  something unexpected and a step errors, the run stops and surfaces exactly where,
  instead of plowing ahead.
- The planning step is pure bookkeeping. It does no network calls and touches no
  private contact information; it just decides what would be typed. The sensitive
  customer details are handled separately and, per the project's own written
  contract, are kept out of the chat summaries and the activity log.

## What it flagged (two low items, both non-issues on a closer look)

A real review is not a rubber stamp, so it surfaced the two things worth a look,
then did the look:

- The diagnostic messages the planner produces can include the value of a field,
  so a reviewer should confirm no genuinely private field's value can ever ride
  along into a place that is meant to stay private. On a closer look the fields
  that carry these values are fixed menu choices, not personal information, and the
  customer's contact details are handled on a separate path. Noted, then cleared,
  with a "confirm this again if the field types ever change" left behind.
- A minor housekeeping note: one timestamp is stamped from the clock at run time,
  which makes that one value non-repeatable between runs. Harmless, overridable,
  not a security issue. Mentioned for completeness, not a flaw.

## What it correctly told me it could NOT check

This is the part a confident-sounding AI review usually hides, and it is the
reason the folder exists. Reading the code proves the machine has no way to
submit. It does not prove the live machinery behaves, so the report handed back
the full list, including:

- The actual browser-driving layer was not read in this pass. The code above
  proves no submit is ever requested, but proving that the "save" really only
  saves, that the typing lands in the right boxes, and that the run opens the
  correct record needs a live test against the real outside system.
- A full trace of where every diagnostic message and log entry ends up, by reading
  every place that consumes them, to prove private data never surfaces somewhere it
  should not. This pass read the engine, not every screen that displays its output.
- That the per-variant settings are correct, so the "stop, a human finishes this"
  marker always lands on the true final step and never one page early or late.
- An end-to-end live run that proves the right data lands on the right record and
  that nothing is committed. The code shows the controls; only a live run proves
  they hold.
- The test suite was read, not executed.

None of these are failures. They are the work a static review hands back on
purpose, named in full so nothing looks covered that was not.

## The takeaway

The scariest kind of automation is the kind that reaches into a real system and
does something you cannot take back. For this one, Vibe Check answered the only
question that matters first, can it do the irreversible thing by accident, and the
answer is no, proven three ways in the code, one of them a test that breaks the
build if the promise is ever weakened. Then it refused to overclaim, and handed
back the exact live tests still needed before anyone calls it bulletproof. That is
the difference between "it ran" and "it is safe," which is the whole point of the
folder.
