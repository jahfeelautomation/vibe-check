# Case study: running Vibe Check on a real production app

The synthetic `demo-target/` is rigged to fail, so it proves the gate blocks a
bad build. This is the other half: what Vibe Check does on a real, shipped app
that is actually maintained. We ran it on one of our own production apps, a real
operations tool we build and run for a paying business. Everything below is from
that real run, sanitized. No product name, no client name, no file paths, no
routes, no integration names, no code, no secrets. Category level only.

It is deliberately undramatic. The honest result on a mature app is not "it found
a critical bug." It is "it confirmed the security posture held, flagged two
low-severity non-issues, and handed back a complete list of what a static review
cannot prove." That last part is the point.

## How it was run

Same folder, audit mode. A Claude Code session was pointed at the Vibe Check
folder and the real project. It read the code; it never ran the app. One pass
over the parts that matter: dependency and config setup, authentication, access
control and roles, multi-tenant isolation, the database layer, and the test
surface. Then it drafted the Build Review Report and gated the draft.

## What it confirmed (the hardening held)

A senior reviewer's worry list, checked and cleared at the static level:

- Authentication is deny-by-default. No valid session, no entry, and a session
  that points at a deleted account is rejected too. Login secrets are stored
  with a slow, modern hash at the current OWASP baseline, not in readable form.
  Session tokens are long random values, expire, and are cleaned up.
- There is one shared scrubber that strips the password hash and the sign-in
  identity from login-account records before they go to a client, with a code note
  on why each field is sensitive. It is applied by convention at the spots that
  return those records. That pattern is what closes the password-leak class that
  sinks the demo app; proving it is applied at every such spot needs a fuller pass
  than this bounded read did, which is exactly the honest caveat the tool is built
  to keep.
- Tenant isolation fails closed. If the code that scopes a request to one
  business is somehow skipped, the request errors out instead of running
  unscoped.
- Role-based access is a default-deny allowlist. A restricted user can reach only
  the surfaces explicitly opened to them; anything not on the list, including any
  route added in the future, is denied automatically rather than leaking.
- Client-side role checks are documented, in the code, as cosmetic only, with the
  server as the real boundary. Trusting the client is the single most common
  vibe-coded security mistake, and it is explicitly avoided here.
- In the paths reviewed: no injectable database queries, no shelling out, no eval,
  no secrets pasted into the source. Secrets live in environment variables; the
  example config ships empty.
- A large automated test suite, with tests sitting right next to every
  security-critical path.

## What it flagged (two low items, both non-issues on inspection)

A real review is not a rubber stamp, so it surfaced the two things worth a look,
and then it did the look:

- The one place in the whole codebase that renders raw HTML. On inspection it is
  the standard pattern from a well-known charting library, fed only by
  developer-written theme settings with no user input, and it sits in a
  non-production sandbox. Noted, then cleared. This is exactly the "check this,
  then move on" a careful reviewer does out loud instead of silently.
- A small performance note for later (a database write that happens on every
  signed-in request). Correct for security, worth revisiting only if traffic
  grows. Not a flaw.

## What it correctly told me it could NOT check

This is the part a confident-sounding AI review usually hides, and it is the
reason the folder exists. The report reproduced the full list of things a read of
the code structurally cannot settle, including:

- Live attack testing against a running copy.
- A real two-account test that proves one user cannot reach another's data end to
  end. The code shows the controls; only a live test proves they hold.
- A data-flow and compliance pass on the customer and payment information the app
  handles, by a person, not self-certified.
- Operational readiness: alerting under real traffic, an incident runbook, and a
  backup that has actually been restored and checked.

None of these are failures. They are the work a static review hands back on
purpose, named in full so nothing looks covered that was not. On this app, that
list is now the real to-do, and we know it because the tool refused to pretend
otherwise.

## The takeaway

For an app we already shipped, Vibe Check did the two things we could not do for
ourselves: it confirmed, at a senior level, that the security work we thought was
in place actually is, and it drew a hard line around what we still have to verify
with a running system and a human. A worried builder gets the same two things:
an honest read of what is solid, and a complete, un-padded list of what is still
open, instead of a green check that means nothing.
