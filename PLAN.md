# Plan: done in 6 days

Team: **Naya** (backend, security, AI layer) and **Nadeem** (frontend, plus
full vertical slices for self-contained modules).

Deadline: Replit Core ends **Thu 3 Dec**. Code is complete on **Wed 2 Dec**.
Thu 3 Dec is the buffer, the freeze, and a check that a clean clone runs
without Replit.

Last verified against `main` on Fri 27 Nov: CI green, 193 backend tests pass,
ruff and mypy clean.

Check progress any time: `make status` (or ask Claude to check the repo).

## Done (verified on main)
- [x] [Both] Foundation: scaffold, CI, AI gateway with mock provider (#3, #4)
- [x] [Naya] Auth backend: users, sessions, roles, seed script (#7)
- [x] [Nadeem] Login and register screens, English and Arabic (RTL), wired to the real API (#5, #6, #9)
- [x] [Naya] Consent, audit log, patient profile, authorization matrix tests (#8, #10)

## Demo scope
**Must:** appointments with no double booking; invoices; drug search with
interaction checker and "unverified" labels; lab results with reference-range
flags; AI assistant (citations, keyword emergency triage, golden set, mock
provider); quiz with only published questions; profile, consent and access-log
screens; hardening; demo.

**Should:** CSV drug import with error report; Jitsi link on appointments;
clinic staff scoping; dashboard counts.

**Cut (after the demo):** radiology and image archive, OCR, SMS and push,
doctor-patient chat, chronic-disease charts, medication reminders,
model-based triage, extra education content.

**Never cut:** authorization matrix tests, audit log, consent, emergency
escalation tests, the "unverified" label, synthetic-data flags.

## Sprint

### Fri 27 Nov: appointments and patient screens
- [ ] [Naya] Appointments backend: doctor profile, availability slots, booking state machine (requested, confirmed, completed, cancelled), no double booking (two simultaneous bookings test), Jitsi link, authorization matrix
- [ ] [Nadeem] Screens: patient profile, consents (grant, revoke, list), my access log, English and Arabic
- [ ] [Both] Merge the workflow upgrade PR; both can run the project without Replit (docs/DEV_ENVIRONMENT.md)
- [ ] [Both] AI provider feasibility test, VPN off first; record in DECISIONS.md

Exit gate: two people booking the same slot, exactly one succeeds; a patient can grant and revoke access from the UI.

### Sat 28 Nov: clinic and invoices
- [ ] [Naya] Clinic, staff scoping, services; invoices (cash, manual paid) and payments ledger; staff see only their own clinic
- [ ] [Nadeem] Booking screens (find a doctor, pick a slot, confirm); invoice screens

Exit gate: booking to invoice works end to end; no cross-clinic leakage.

### Sun 29 Nov: AI layer part 1 and pharmacy
- [ ] [Naya] Real provider behind the gateway (chosen by the feasibility test), timeouts, retries, fallback to mock, caching; embeddings and pgvector: ingest, retrieve, answer with citations
- [ ] [Nadeem] Pharmacy slice: drug schema with source and verification status, 20 to 30 fake drugs, interaction rules and checker, alternatives (same ingredient and strength), search screen

Exit gate: known-pair test passes (A+B severe, A+C none); nothing unverified shown as fact.

### Mon 30 Nov: AI layer part 2 and lab
- [ ] [Naya] Safety layer: keyword emergency triage before any model call, blocked outputs, disclaimers, prompt versioning, golden set of 40 with a runner, prompt-injection test
- [ ] [Nadeem] Lab slice: tests, reference ranges by age and sex, high/low flags at boundaries, manual result entry, results view, private file upload with type and size limits

Exit gate: 100% of emergency cases escalate; no dose without a verified source; boundary flag tests pass.

### Tue 1 Dec: education, assistant screen, hardening starts
- [ ] [Nadeem] Education slice: question bank (draft, reviewed, published), quiz engine, one branching case, only published questions reach students; assistant chat screen
- [ ] [Naya] Dashboard counts (appointments, patients, revenue); login rate limiting, CORS, security headers, secrets check; Postgres trigger making audit_logs append-only; dependency audits clean

Exit gate: a student finishes a quiz and a case; unreviewed content is never shown.

### Wed 2 Dec: hardening, tests, demo
- [ ] [Both] Playwright: login in Arabic, booking, quiz
- [ ] [Both] Break-it session (wrong IDs, no login, bad input); fix findings; full regression green in CI
- [ ] [Naya] "Fill with real data" guide: remove synthetic data, CSV import for drugs and ranges, production secrets, hosting
- [ ] [Nadeem] Demo script, user guide per role, known-limitations list
- [ ] [Both] Tag release v0.1.0-demo

Exit gate: no critical or high issue open; the demo runs end to end.

### Thu 3 Dec: buffer (Replit Core ends)
- [ ] [Both] Finish slipped items and freeze main
- [ ] [Both] Verify a clean clone runs on a machine without Replit

## If we fall behind
If the previous day's exit gate is not green by 18:00, cut from the Cut list
first, then from Should. Do not cut anything on the Never cut list.

## Risks
- Six days for seven modules is aggressive. Pharmacy, lab and education are
  about one day each, and only work if they reuse the patterns already in the
  repo (docs/MODULE_CHECKLIST.md).
- AI provider access from Syria is unverified until the feasibility test.
- Unit tests run on SQLite; the new `migrations` CI job runs the migrations
  on real Postgres. Watch it.
- Nadeem takes backend slices for pharmacy, lab and education. Naya reviews
  anything that touches authorization, consent, audit or migrations.
