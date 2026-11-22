# Project brief

## What it is
A Medical Super App for Syria, built in 10 days by two people using AI as a
fast junior developer. Every module is a thin vertical slice on synthetic
data, ready to be filled with real data later.

## Users (roles)
patient, doctor, clinic admin, pharmacist, student, lab/radiology staff,
super admin.

## Modules
1. Core platform and medical record: auth, roles, patient profile, files,
   consent, audit log.
2. Digital care: doctors, appointments, chat (polling), Jitsi links,
   chronic tracking.
3. Clinic business: staff, invoices, payments ledger, basic dashboard.
4. Pharmacy: drug database, interactions, alternatives, reminders.
5. Laboratory and radiology: results (manual entry), reference ranges,
   flagging, image upload and archive.
6. AI layer: grounded assistant (RAG with citations), safety layer,
   evaluation golden set.
7. Medical education: question bank, quizzes, one branching case,
   review status.

## In scope
Thin vertical slices, Arabic (RTL) and English, PWA, authorization matrix,
audit log, consent, emergency escalation tests.

## Out of scope (cut for 10 days)
OCR (manual entry only), radiology extras, model-based triage (keyword
triage only), SMS/push, dashboard extras, large education content,
doctor review of AI outputs (after the 10 days).

## Hard rules
- Synthetic data only. Every fake record has is_synthetic = true.
- No real patient data ever enters this repo or any AI chat.
- The app is informational. It does not diagnose.
- Constraints: users in Syria, unreliable internet and power, so keep
  payloads small and design for low bandwidth.
