#!/usr/bin/env python3
"""
Vibe Check - the blocking gate.

INVARIANT (enforced here, not left to prose):
  The Build Review Report never calls the build "secure" or "ready" while a
  serious finding is unresolved, AND it always discloses its full declared
  coverage: every could-not-check item (CNC-01..CNC-13) and every lifecycle
  phase (PHASE-1..PHASE-7) must be present.

This is a CANONICAL FLOOR, not total coverage. It catches the common shapes of
the failure, not every phrasing. The discipline in rules.md carries the rest.

Usage:
  python check.py path/to/report.md     # gate one report (exit 0 pass / 1 fail)
  python check.py -                      # read report from stdin
  python check.py --self-test            # run the regression suite (exit 0/1)

Stdlib only. No network. No third-party deps.
"""

import re
import sys

# --- canonical coverage tokens the report MUST contain ----------------------
CNC_IDS = [f"CNC-{n:02d}" for n in range(1, 14)]   # CNC-01 .. CNC-13
PHASE_IDS = [f"PHASE-{n}" for n in range(1, 8)]     # PHASE-1 .. PHASE-7

# --- verdict grammar --------------------------------------------------------
_SUBJECT = r"(?:this build|the build|this app|the app|this project|the project|it)"
_COPULA = r"(?:is|looks|seems|appears)"
_READY = (r"(?:secure|safe to ship|safe to deploy|production[-\s]?ready|"
          r"ready to ship|ready to deploy|ready for production)")
_ASSERTION = re.compile(rf"\b{_SUBJECT}\s+{_COPULA}\s+(?:now\s+)?{_READY}\b",
                        re.IGNORECASE)
_BARE = re.compile(
    r"\b(?:no (?:security )?issues found|no issues found|nothing to fix|"
    r"all clear|good to go|safe to ship)\b", re.IGNORECASE)
_SCOPED_AFTER = re.compile(r"\s+(?:in|with|for|within|on)\b", re.IGNORECASE)
_NEG_BEFORE = re.compile(
    r"(?:not|never|isn't|aren't|won't|wouldn't|once|after|until|unless|when|"
    r"if|no longer|not yet)\b[^.?!]{0,40}$", re.IGNORECASE)

# A *serious finding* is a fix-list item whose leading label (after the bullet)
# is CRITICAL, HIGH, or COULD-NOT-VERIFY, followed by a colon. Matching only this
# finding shape is deliberate: it keeps the trigger words from firing when they
# appear in report boilerplate (the verdict note, a format legend, or prose like
# "no Critical or High findings remain"). Case-sensitive on purpose, because the
# convention is that real finding labels are uppercase.
_SERIOUS_FINDING = re.compile(r"\s*[-*]\s+(?:COULD-NOT-VERIFY|CRITICAL|HIGH)\s*:")
_RESOLVED = re.compile(r"\[RESOLVED\]", re.IGNORECASE)
_VERDICT = re.compile(r"^\s*Verdict:\s*(GO|NO-GO)\b",
                      re.IGNORECASE | re.MULTILINE)


def _has_open_serious(text):
    """True if any fix-list finding is an open CRITICAL/HIGH/COULD-NOT-VERIFY:
    finding-shaped (bullet + uppercase label + colon) and not tagged [RESOLVED].
    Boilerplate mentions of those words do not count - only actual findings."""
    for line in text.splitlines():
        if _SERIOUS_FINDING.match(line) and not _RESOLVED.search(line):
            return True
    return False


def _readiness_claim(text):
    """Return the first readiness assertion that is not negated/conditional/
    scoped, else None."""
    for m in _ASSERTION.finditer(text):
        head = text[:m.start()]
        prefix = head.splitlines()[-1] if head else ""
        if _NEG_BEFORE.search(prefix):
            continue
        return m.group(0)
    for m in _BARE.finditer(text):
        tail = text[m.end():m.end() + 12]
        if _SCOPED_AFTER.match(tail):
            continue
        head = text[:m.start()]
        prefix = head.splitlines()[-1] if head else ""
        if _NEG_BEFORE.search(prefix):
            continue
        return m.group(0)
    return None


def gate(text):
    """Return (passed, violations)."""
    violations = []

    # Completeness of disclosure (the load-bearing check).
    for cid in CNC_IDS:
        if cid not in text:
            violations.append(f"INCOMPLETE: missing could-not-check item {cid}")
    for pid in PHASE_IDS:
        if pid not in text:
            violations.append(f"INCOMPLETE: missing lifecycle phase {pid}")

    open_serious = _has_open_serious(text)

    # Verdict grammar A: structured verdict field vs open serious finding.
    vm = _VERDICT.search(text)
    if vm and vm.group(1).upper() == "GO" and open_serious:
        violations.append(
            "OVERCLAIM: Verdict is GO while a CRITICAL/HIGH or COULD-NOT-VERIFY "
            "finding is still open.")

    # Verdict grammar B: prose readiness assertion vs open serious finding.
    claim = _readiness_claim(text)
    if claim and open_serious:
        violations.append(
            f'OVERCLAIM: readiness claim ("{claim.strip()}") while a serious '
            "finding is still open.")

    return (len(violations) == 0, violations)


# --- regression suite -------------------------------------------------------
_FULL_DISCLOSURE = (
    "## What I could NOT check\n"
    + "\n".join(f"- {c}: (runtime or human item)" for c in CNC_IDS)
    + "\n## Lifecycle coverage\n"
    + "\n".join(f"- {p}: reviewed" for p in PHASE_IDS)
    + "\n"
)


def _report(verdict, body):
    return f"Verdict: {verdict}\n\n{body}\n\n{_FULL_DISCLOSURE}"


def _drop(token, ids, label):
    body = "Fix list: none.\n\n## What I could NOT check\n" + "\n".join(
        f"- {c}: x" for c in CNC_IDS if not (ids is CNC_IDS and c == token))
    body += "\n## Lifecycle coverage\n" + "\n".join(
        f"- {p}: reviewed" for p in PHASE_IDS if not (ids is PHASE_IDS and p == token))
    return "Verdict: GO\n\n" + body + "\n"


SAMPLES_FAIL = [
    # GO while an open CRITICAL exists (structured verdict gate).
    ("go-with-open-critical",
     _report("GO", "Fix list:\n- CRITICAL: hardcoded API key in client bundle.")),
    # NO-GO field but prose claims the build is secure, with an open HIGH.
    ("prose-secure-with-open-high",
     _report("NO-GO", "This build is secure.\nFix list:\n- HIGH: missing auth on /admin.")),
    # "Safe to ship" while a COULD-NOT-VERIFY finding is open.
    ("safe-to-ship-with-cnv",
     _report("GO", "Safe to ship.\nFix list:\n- COULD-NOT-VERIFY: token expiry unclear.")),
    # Missing a could-not-check item (drops CNC-07) - completeness gate.
    ("missing-cnc-07", _drop("CNC-07", CNC_IDS, "cnc")),
    # Missing a lifecycle phase (drops PHASE-5) - completeness gate.
    ("missing-phase-5", _drop("PHASE-5", PHASE_IDS, "phase")),
]

SAMPLES_PASS = [
    # Clean GO: no serious findings, full disclosure.
    ("clean-go", _report("GO", "Fix list:\n- LOW: tighten a log message.")),
    # Honest NO-GO: open CRITICAL, no readiness claim - must PASS.
    ("honest-no-go",
     _report("NO-GO", "Fix list:\n- CRITICAL: SQL injection in search.")),
    # Conditional readiness - near-miss, must PASS.
    ("conditional-ready",
     _report("NO-GO", "Once these three are fixed it will be ready to ship.\n"
                      "Fix list:\n- HIGH: weak password hashing.")),
    # Negated readiness - near-miss, must PASS.
    ("negated-ready",
     _report("NO-GO", "This build is not yet secure.\nFix list:\n- HIGH: open CORS.")),
    # Scoped 'no issues' - near-miss, must PASS even with an open CRITICAL.
    ("scoped-no-issues",
     _report("NO-GO", "No issues in the auth module.\nFix list:\n- CRITICAL: RCE in upload.")),
    # Resolved serious finding + GO - must PASS (it's fixed).
    ("go-with-resolved",
     _report("GO", "Fix list:\n- CRITICAL: hardcoded key [RESOLVED] rotated to env.")),
    # Clean GO that contains the real report boilerplate: the verdict note, a
    # pipe-style severity legend, and a prose mention of COULD-NOT-VERIFY. The
    # trigger words appear in boilerplate, not in findings, so the gate must NOT
    # block it. This is the regression that makes a green self-test mean "real
    # reports pass," not just "minimal shapes pass."
    ("clean-go-real-template",
     "Verdict: GO\n"
     "(NO-GO if any Critical or High finding is still open.)\n\n"
     "## Fix list (worst first)\n"
     "Each finding begins with its severity in capitals.\n"
     "- CRITICAL | HIGH | MEDIUM | LOW: short problem. Location: file:line. "
     "Fix: instruction. Use COULD-NOT-VERIFY for a serious item not confirmable "
     "from a static read.\n"
     "- LOW: tighten a verbose log line.\n\n" + _FULL_DISCLOSURE),
]


def self_test():
    ok = True
    for name, text in SAMPLES_FAIL:
        passed, _ = gate(text)
        if passed:
            ok = False
            print(f"FAIL-SAMPLE NOT BLOCKED: {name}", file=sys.stderr)
    for name, text in SAMPLES_PASS:
        passed, v = gate(text)
        if not passed:
            ok = False
            print(f"PASS-SAMPLE WRONGLY BLOCKED: {name} -> {v}", file=sys.stderr)
    if ok:
        print(f"self-test OK: {len(SAMPLES_FAIL)} fail-samples blocked, "
              f"{len(SAMPLES_PASS)} pass-samples cleared.")
    return ok


def main(argv):
    if len(argv) != 1:
        print("usage: check.py <report.md | - | --self-test>", file=sys.stderr)
        return 2
    arg = argv[0]
    if arg == "--self-test":
        return 0 if self_test() else 1
    text = sys.stdin.read() if arg == "-" else open(arg, encoding="utf-8").read()
    passed, violations = gate(text)
    if passed:
        print("GATE PASSED: the report is honest and complete about its coverage.")
        return 0
    print("GATE FAILED - this report may not be shown:", file=sys.stderr)
    for v in violations:
        print(f"  - {v}", file=sys.stderr)
    print("\nFix: resolve or honestly disclose the item above. A GO verdict "
          "requires no open CRITICAL/HIGH and a complete coverage disclosure.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
