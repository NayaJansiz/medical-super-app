# Schema (draft: names and relationships only)

Conventions: every table has id, created_at, updated_at; seeded rows have
is_synthetic = true.

## Core (Module 1)
- users (role, email, password_hash, full_name, is_active) [built Day 2]
- sessions (user_id, token_hash, expires_at, revoked_at) [built Day 2]
- organizations; memberships (user, organization, role)
- patient_profiles (user_id unique, allergies, surgeries, medical_history,
  medication_history) [built Day 3]. patient_id everywhere = patient_profiles.id
- files (owner, patient_id, type, size, private storage path)
- consents (patient_id, grantee_user_id, scope, expires_at, revoked_at)
  [built Day 3]. scope: records:read | records:write (write includes read);
  expires_at required, at most 365 days ahead
- audit_logs (actor_id, action, resource_type, resource_id, patient_id,
  at, outcome, detail) [built Day 3]. Append-only, no foreign keys, no
  updated_at. outcome: success | denied. detail: short text, never patient content

## Digital care (Module 2)
- doctor_profiles (user_id, specialty); availability_slots
- appointments (patient, doctor, slot, status, jitsi_url)
  status: requested -> confirmed -> completed | cancelled
- chat_messages (appointment or thread, sender, body)
- chronic_readings (patient, type [glucose|bp|weight], value, taken_at)
- notifications

## Clinic business (Module 3)
- clinics (organization); clinic_staff; services_rooms
- invoices (appointment, patient, amount, status); payments_ledger

## Pharmacy (Module 4)
- drugs (brand, active_ingredient, strength, form, manufacturer,
  indications, contraindications, dose_guidance, source,
  verification_status)
- interaction_rules (ingredient_a, ingredient_b, severity, source,
  verification_status)
- medication_reminders; adherence_logs

## Lab and radiology (Module 5)
- lab_tests; reference_ranges (test, age band, sex, low, high)
- lab_results (patient, test, value, flag, entered_by, confirmed)
- imaging_studies (patient, modality, file_id, metadata)

## AI (Module 6)
- documents; chunks (embedding vector); ai_requests (task, provider,
  tokens, latency, cache_key); golden_set_results

## Education (Module 7)
- courses; lectures; tags
- questions (options, correct, explanation, source, difficulty,
  review_status [draft|reviewed|published])
- quiz_attempts; cases; case_nodes (branching)
