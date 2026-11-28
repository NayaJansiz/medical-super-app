# Current phase

The plan lives in PLAN.md. This file holds only today's task cards.

## Fri 27 Nov: appointments and patient screens

### Naya: appointments backend
- Goal: a patient books a doctor's slot, the state moves through
  requested, confirmed, completed, cancelled, and two people cannot book the
  same slot.
- Acceptance criteria:
  1. Doctor profile and availability slots (create and list).
  2. Booking state machine with only legal transitions.
  3. Double booking prevented (test with two simultaneous bookings).
  4. Jitsi link attached to a confirmed appointment.
  5. Authorization matrix: each role against each endpoint; patients see
     only their own appointments; every read and write is audited.
- Out of scope: chat, reminders, payments.
- Test: `make check`; try booking the same slot twice.

### Nadeem: patient screens
- Goal: a patient manages their own profile, consents and access log from the UI.
- Acceptance criteria:
  1. Profile page (view and edit) using `/api/v1/patients/me/profile`.
  2. Consents page: grant to a doctor by email with scope and expiry, list,
     revoke (`/api/v1/consents`, `/consents/{id}/revoke`).
  3. Access log page using `/api/v1/audit-logs/me`.
  4. English and Arabic (RTL), works at 360px width, clear error messages.
- Out of scope: doctor screens.
- Test: `pnpm --dir frontend build`; click through as `patient@demo.example`.

### Both
- Merge the workflow upgrade PR; run `make status` to see the plan.
- Both can run the project outside Replit (docs/DEV_ENVIRONMENT.md).
- AI provider feasibility test, VPN off first; record in DECISIONS.md.
