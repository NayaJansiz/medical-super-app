# How Naya and Nadeem work

Two senior engineers, six days, one repo. Short rules, applied every day.

| | GitHub | Focus |
|---|---|---|
| Naya | @NayaJansiz | Backend, security, AI layer, hardening |
| Nadeem | @nadeembrijawy | Frontend, full vertical slices (pharmacy, lab, education), end-to-end tests |

Focus is not ownership. Either of us can change anything, through a PR.

## The loop (every task)
1. Pick the next unchecked item in PLAN.md. Write a task card in the PR
   description: goal, acceptance criteria, out of scope, how to test.
2. Branch `feat/<name>`, small commits (`feat:`, `fix:`, `test:`, `docs:`,
   `chore:`, `ci:`). Keep PRs under about 400 changed lines.
3. Tests first for bugs. A feature ships with happy path, validation failure
   and an authorization matrix (every role against every endpoint).
4. `make check` must pass locally. Push. CI must be green.
5. Merge (squash), tick the box in PLAN.md in the same PR, delete the branch.

## Review: by risk, not by ritual
- **The other person must approve before merge:** anything in auth, consent
  and records authorization, audit, the AI safety layer, `core/security.py`,
  Alembic migrations that change existing tables, `.github/`, `SAFETY_RULES.md`.
  CODEOWNERS requests the review automatically.
- **Self-merge on green CI:** screens, new modules that follow the pattern,
  docs, tests. The other person may still comment after the merge, and the
  author fixes follow-ups in a new PR.
- **Second AI tool:** security-sensitive diffs also go to a different AI
  tool with the Security review prompt (PROMPTS.md) before merge.
- Review the code, not the person. Say what is wrong and how to test it.

## Communication
- Morning (10 min): who does what today, what could block it.
- Evening (10 min): run `make status`, update PLAN.md, say done, blocked,
  learned, risks. Write it in DAILY_LOG.md if you want a record.
- Stuck for 15 minutes: ask. After 3 failed AI fixes: stop, summarize, start a
  fresh chat with the Debugger prompt.
- Decisions go in DECISIONS.md with the reason. If it is not written down, it
  did not happen.

## Standards (both of us hold the line)
- No secrets in code or chats. No real patient data anywhere. Every fake
  record has `is_synthetic = true`.
- Every endpoint states who may call it and enforces it on the server.
- Unverified medical content is labelled "unverified" in the UI.
- Migrations only through Alembic. Never edit the database by hand.
- A bug gets a failing test first, then the fix.
- Main is always green. If main breaks, fixing it is the only priority.

## Working hours
Fixed hours, real breaks, no all-nighters before the AI days (Sun 29 and
Mon 30). Tired people write the bugs the tests do not catch.

## AI tools
Claude Project: design, review, security review. ChatGPT or Gemini: bulk code
and tests after the design is approved. A different tool reviews than wrote.
Replit Agent is not used. See PROMPTS.md and AGENTS.md.
