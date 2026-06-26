# Coverage map: the seven lifecycle phases

Vibe Check organizes its review along the full life of a software project. Each
phase carries a detectability tag for every check: CAN-DETECT (provable from a
static read), NEEDS-RUNTIME (needs a running system), NEEDS-HUMAN (needs a human
decision). NEEDS-RUNTIME and NEEDS-HUMAN items are exactly the could-not-check
manifest (see 01). Checks trace to named frameworks, not invention: OWASP SAMM
v2.0, NIST SSDF SP 800-218 v1.1, OWASP Top 10:2025, OWASP ASVS 5.0.0.

| ID | Phase | What gets looked at | Framework anchor |
|----|-------|---------------------|------------------|
| PHASE-1 | Plan / Requirements | Is there a stated purpose, threat model, and data inventory? | SAMM Governance; SSDF PO |
| PHASE-2 | Design / Architecture | Trust boundaries, authn/authz model, secret handling, dependencies | SAMM Design; Top 10 A06 Insecure Design |
| PHASE-3 | Coding / Implementation | Injection, secrets in code, input handling, crypto use | Top 10 A05/A04/A03; ASVS |
| PHASE-4 | Code Review / Verification | Is anything reviewing changes? Are there obvious unguarded paths? | SAMM Implementation; SSDF PW |
| PHASE-5 | Testing | Test presence and shape, security-relevant tests, coverage gaps | SSDF PW.7/PW.8 |
| PHASE-6 | Deployment / Release | Config, debug flags, exposed services, supply-chain integrity | Top 10 A02/A08; SSDF PS |
| PHASE-7 | Operations / Monitoring | Logging, alerting, incident response, backups, rotation | Top 10 A09; SAMM Operations |

Every Build Review Report addresses all seven phases by ID. check.py asserts
each PHASE-n appears. A phase with nothing to flag still gets a one-line "looked,
clean" so the reader can see it was not skipped.
