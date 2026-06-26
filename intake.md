# Intake: how you read a project

When handed a project, read it in this order. Each stop says what you are
looking for. You are building the picture yourself, from the repository, not
from the user.

## Read order

1. **Manifests and lockfiles** (`package.json`, `requirements.txt`, `go.mod`,
   `Gemfile`, lockfiles, etc.)
   Learn the stack, the dependencies, and the scripts. Note floating versions,
   missing lockfiles, and anything install/build runs automatically.

2. **Config and environment** (`.env` files, `config/`, Docker files, CI
   workflows)
   Look for secrets committed into the repo, debug flags left on, and services
   exposed by configuration. A real key in a tracked file is a finding on sight.

3. **Entry points and routes**
   Map what is reachable from outside and what is public versus authenticated.
   Build the list of endpoints before judging any one of them.

4. **Auth and access control**
   How is identity established, and how are permissions enforced on each
   sensitive route? Separate "who are you" from "are you allowed to do this," and
   confirm both exist server-side, not just in the UI.

5. **Data layer**
   Read the queries (string-built queries are injection risk), note what data is
   stored, and trace where it flows. Flag anything sensitive that moves without
   protection.

6. **Tests**
   Are there tests, what shape are they, and do any of them exercise the
   security-relevant paths? Presence is not the same as coverage; judge both.

7. **Deploy and release config**
   How does it ship, and is the supply chain it pulls from trustworthy and
   pinned? Look at how production differs from local.

## The rule for every unknown

Every unknown you hit during intake becomes a check-it-yourself task in the
report. If settling it needs a running system or a human decision, map it to the
matching could-not-check item (`reference/01-could-not-check-manifest.md`) and
disclose it there. It never becomes a question handed back to the user. The user
came to you because they cannot answer those questions; answering for them, or
honestly marking what cannot be answered from a static read, is the whole point.
