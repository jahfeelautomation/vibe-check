# Worked examples

Four situations and the slice of the Build Review Report each produces. These
show the voice and the format from `rules.md`, and they match what `check.py`
allows and blocks. The disclosure sections are abbreviated here for space; a real
report reproduces the full could-not-check manifest (CNC-01 through CNC-15) and
all seven lifecycle phases, which is what lets an honest report pass the gate.

## Example 1: a CRITICAL finding with an exact fix

Situation: a React app reads its database credentials from a value bundled into
the client JavaScript, so anyone who opens the site can read the key and write
to the database.

Report slice:

```
- CRITICAL: the database service key is shipped in the client bundle, so any
  visitor can read it from their browser and write to your database. Location:
  src/lib/db.js:12. Fix: remove the key from client code, move all database
  calls behind a server endpoint that holds the key in a server-side environment
  variable, then rotate the exposed key because it must be treated as already
  leaked.
```

Note the shape: severity first, the harm in plain English, the exact location,
then an instruction the user's Claude Code can act on. No adjectives; the fact
carries it.

## Example 2: an honest NO-GO that PASSES the gate

Situation: the audit found a real SQL injection. The build is not ready, and the
report says so. Because it does not claim the build is secure or ready, and it
discloses its full coverage, the gate lets it through. Honesty is what passes,
not a clean result.

Report slice:

```
**BUILD REVIEW REPORT: order-portal, audit, 2026-06-25**

Verdict: NO-GO
(NO-GO if any Critical or High finding is still open.)

## Fix list (worst first)
- CRITICAL: the search box builds its SQL by pasting the typed text straight
  into the query, so a crafted search can read or change any table. Location:
  server/search.py:41. Fix: switch to a parameterized query (pass the search
  text as a bound parameter, never string-concatenated).

## What I could NOT check (do these yourself)
(full manifest CNC-01 through CNC-15 reproduced here)

## Lifecycle coverage
PHASE-1 through PHASE-7, one line each.

## Bottom line
One real Critical issue stands between this and safe to run. Fix the search
query, re-run, and this becomes a GO.
```

This passes `check.py`: the verdict is NO-GO, there is no "secure" or "ready"
claim, and the disclosure is complete.

## Example 3: a near-miss that PASSES (conditional readiness)

Situation: the report wants to point at the finish line without lying. Saying it
"will be ready once these are fixed" is a conditional, not a present claim that
the build is ready, so the gate allows it even though a HIGH is still open.

Report slice:

```
Verdict: NO-GO
(NO-GO if any Critical or High finding is still open.)

## Fix list (worst first)
- HIGH: passwords are stored with a fast hash (sha1), which is quick to crack if
  the database leaks. Location: server/auth.py:88. Fix: rehash with bcrypt or
  argon2 and migrate existing users on next login.

## Bottom line
Once the password hashing and the two other High items are fixed, this will be
ready to ship. It is not there yet.
```

"Once ... it will be ready" is conditional. A present-tense "this is ready to
ship" with the same open HIGH would be blocked by the gate. The difference is
the whole discipline in one line.

## Example 4: gate mode (one new change before trusting it)

Situation: the user added a file-upload feature and wants it checked before they
rely on it. The review is scoped to the change and what it can reach, not the
whole app.

Report slice:

```
**BUILD REVIEW REPORT: order-portal, gate of "add receipt upload", 2026-06-25**

Verdict: NO-GO
(NO-GO if any Critical or High finding is still open.)

## Fix list (worst first)
- HIGH: the upload accepts any filename and saves it under the web root, so a
  visitor can upload a script and then request it to run it. Location:
  server/upload.py:23. Fix: store uploads outside the web root, generate a random
  server-side filename, and allow only an explicit list of file types.
- COULD-NOT-VERIFY: whether oversized or malformed files are rejected. Throwing
  hostile inputs at a parser needs a running system (CNC-04). Test it before you
  trust the feature.

## Bottom line
The upload feature is not safe to trust yet. One High to fix, and one runtime
test you need to run yourself.
```

Gate mode keeps the report tight: it judges the change, names what the change
can reach, and still discloses the runtime checks it could not run.
