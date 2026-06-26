# Could-not-check manifest

These are the things a static read of code, config, and git history genuinely
CANNOT settle. They need a running system or a human decision. Every Build
Review Report reproduces this entire list under "What I could NOT check", so the
user is never fooled into thinking a category was covered when it wasn't. The
IDs are stable; check.py asserts every one appears in the report.

| ID | What it is | How you check it yourself |
|----|------------|---------------------------|
| CNC-01 | Live attack testing (DAST) against a running instance | Run an automated scanner against a staging deploy, or hire a tester. |
| CNC-02 | Runtime access-control / IDOR testing across two real identities | Log in as two different users and try to read each other's data. |
| CNC-03 | Penetration test by a human | Engage a pentester for anything handling money or personal data. |
| CNC-04 | Fuzzing of inputs and parsers | Throw malformed and oversized inputs at every endpoint and file upload. |
| CNC-05 | Live monitoring and alerting under real traffic | Confirm you get paged when error rates or latency spike in production. |
| CNC-06 | TLS / certificate handshake on the deployed endpoint | Test the live domain with an SSL checker; confirm a valid cert and no weak ciphers. |
| CNC-07 | Open-port / exposed-service scan of the live host | Scan the server's public IP; confirm only intended ports are open. |
| CNC-08 | Data classification (what is sensitive, and where it flows) | List what personal or payment data you store and trace where it goes. |
| CNC-09 | Compliance scope (GDPR / HIPAA / PCI and friends) | Ask a professional which regimes apply; do not self-certify. |
| CNC-10 | Threat-model quality (is the stated threat model the right one) | Have someone experienced sanity-check who realistically attacks this and why. |
| CNC-11 | Incident-response readiness (what happens when, not if, it breaks) | Write the one-page "who does what when it goes down" runbook. |
| CNC-12 | Secret rotation and key-management policy over time | Confirm keys can be rotated and that you know how and how often. |
| CNC-13 | Backup and restore actually tested end to end | Restore a backup into a scratch environment and confirm it works. |
| CNC-14 | Secrets that live only on the running server (a deploy token in the server's git config, a value in a server `.env` or shell history, credentials in process listings or logs) | Log into the host and look: check `git config` for an embedded token, the server's `.env`, and shell history. Replace any plaintext token with a least-privilege credential; for code pulls, a read-only deploy key tied to that one project, so a server break-in cannot spread. |
| CNC-15 | Whether a hard spend cap or billing alert is actually set on each paid, metered service (AI API, SMS, maps, storage) | In each vendor's dashboard, set a hard monthly spending limit or a billing alert at a threshold you choose, so a runaway loop or a busy month cannot surprise you with a large bill. |

These fifteen are the floor, not a ceiling. They are the categories a careful
static review can never close on its own, so they are always named in full. If a
specific project surfaces another runtime-or-human unknown, add it as an extra
line in the report; never drop one of these to make a report look cleaner.
