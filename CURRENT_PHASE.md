# Current phase: Day 3 Consent and audit log

Goal: a patient controls who can see their record, and every access is logged.
Focus (one thing): consent + audit log on top of the Day 2 auth and roles.

## Tasks
- [x] Day 1 foundation (scaffold, CI, AI Gateway mock)
- [x] Day 2 auth backend (users, sessions, roles) and login/register screens
- [ ] Day 2 auth PR merged to main (backend) and frontend wired to the real API
- [ ] Day 3 PR: patient profile, consents, audit log, matrix tests
- [ ] Day 3 reviewed by the other person plus a fresh AI chat (Security review prompt)

## Exit gate
A patient grants a doctor access, the doctor reads the profile, the patient
revokes, the doctor gets 404, and the patient sees all of it in their log.

## Status
(update daily; 5-line log: done, blocked, next, learned, risks)
- done: auth backend branch pushed; consent + audit built and tested on a copy
- blocked: nothing; Day 3 branches from main after the auth merge
- next: merge auth, merge Day 3, frontend wires /api, Day 4 appointments
- learned: denials must be audited too, not only successful reads
- risks: no login rate limiting yet (Day 10); no break-glass access (post-demo)

## 10-day roadmap (one focus per day)
1 Foundation | 2 Auth and roles | 3 Consent and audit log |
4 Appointments | 5 Clinic and invoices | 6 Pharmacy | 7 Lab |
8 AI layer | 9 Education | 10 Hardening and demo
