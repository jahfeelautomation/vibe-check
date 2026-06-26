# Area checklists

Nine areas. Each check is something you can settle by reading the code, the
config, or the git history, with no running system. Where a check actually needs
a running system or a human decision, it is tagged with the matching `CNC-xx`
from `01-could-not-check-manifest.md` and belongs in the report's "What I could
NOT check" section, not the fix list. Severities for anything found are decided
in the report, not here.

## Authentication & session
- Is there a single, consistent place that decides who the caller is, or is
  identity re-checked ad hoc in each route?
- Are passwords stored with a slow, salted hash (bcrypt/scrypt/argon2), never
  plaintext, md5, or sha1?
- Do sessions or tokens expire, and is there a logout / revoke path? (Token
  expiry actually firing under load is CNC-02.)
- Are login, password-reset, and token-issuing routes rate-limited or otherwise
  protected from brute force?
- Are session cookies marked HttpOnly, Secure, and SameSite where the framework
  allows it?

## Authorization & access control
- After "who are you" is settled, is "are you allowed to do this" checked on
  every sensitive route, not just the first one?
- Do object lookups scope by owner (e.g. `WHERE id=? AND user_id=?`), or can any
  id be read by anyone? (Confirming this on a live system across two identities
  is CNC-02.)
- Are admin or privileged routes guarded by a real role check, not just an
  unlinked URL?
- Is access control enforced on the server, never only hidden in the UI?

## Secrets & configuration
- Are any credentials, API keys, tokens, or connection strings written as string
  literals in source or committed config?
- Is there a real secret-loading path (environment, vault) rather than hardcoded
  values?
- Does `.gitignore` exclude `.env` and key files, and does git history show no
  previously committed secrets?
- Are debug flags, verbose stack traces, and test backdoors off in the
  production configuration?

## Injection & input handling
- Are SQL/queries built with parameters or an ORM, never string concatenation of
  user input?
- Is shell, OS-command, or template execution ever built from request data?
- Is user input validated and length-bounded at the boundary, and output encoded
  where it lands (HTML, SQL, shell, headers)?
- Are file uploads constrained by type, size, and storage location, and never
  executed? (Exercising the parser with hostile input is CNC-04.)

## Cryptography & data protection
- Is anything sensitive sent or stored without transport security (plain http,
  unencrypted DB fields that should not be plaintext)?
- Are standard libraries used for crypto rather than hand-rolled algorithms?
- Are tokens, salts, and ids generated with a cryptographically secure random
  source, not `Math.random()` or a timestamp?
- Is it clear what data is sensitive and where it flows? (A real data
  classification is CNC-08; the live TLS handshake is CNC-06.)

## Dependencies & supply chain
- Is there a lockfile, and are dependencies pinned rather than floating?
- Do any dependencies have known-vulnerable versions a quick audit would flag?
- Are there unused, unmaintained, or surprising packages pulled in?
- Is install/build wired to run arbitrary scripts from untrusted sources?

## Logging, errors & monitoring
- Do logs avoid writing secrets, passwords, tokens, or full personal records?
- Do errors return a safe message to the caller instead of a full stack trace or
  SQL string?
- Is there logging on the security-relevant events (login, access denied,
  admin action) at all?
- Is there any alerting wired up? (Whether paging actually fires under real
  traffic is CNC-05; incident-response readiness is CNC-11.)

## Scalability & performance
- Are there obvious unbounded queries (no pagination, `SELECT *` over a growing
  table) on hot paths?
- Are there N+1 query patterns or per-request work that grows with total data?
- Are expensive operations done synchronously inside a request that should be a
  background job?
- Are there indexes on the columns that filtering and joins depend on?

## Maintainability & structure
- Is responsibility separated, or is there a single very large file doing
  everything?
- Are concerns (routes, data access, business logic) layered, or tangled
  together so a change ripples everywhere?
- Is configuration centralized, or are magic values and copy-pasted blocks
  scattered through the code?
- Is there enough test presence that a future change can be made with some
  confidence? (Whether the tests actually exercise the risky paths is judged in
  PHASE-5.)
