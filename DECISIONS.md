# Decisions log

| Date | Decision | Why | Who |
|------|----------|-----|-----|
| 2026-11-22 | Trunk-based Git, no develop branch | 2 people, 10 days | both |
| 2026-11-22 | Python/FastAPI backend, React/TypeScript frontend | AI, RAG, OCR and CSV import are the hardest modules and Python's ecosystem is strongest there. Pydantic gives built-in validation. Cost: two languages. | both |
| 2026-11-22 | AGENTS.md in repo is the source of truth for AI instructions | Free Claude Projects are not shared; ChatGPT, Gemini and Replit cannot see them | both |
| 2026-11-22 | uv with lock file | Identical environments on both machines | both |
| 2026-11-25 | Denied access to a patient record returns 404 and is audited as outcome=denied | Does not reveal that a record exists (CONVENTIONS) and leaves a trail of probing | A |
| 2026-11-25 | Consent scopes: records:read and records:write (write includes read); expiry required, max 365 days | Simplest rule that still limits what a doctor can do; per-section scopes later | A |
| 2026-11-25 | Doctors find patient ids through GET /consents/received, not by guessing | Avoids ID enumeration; patient_id = patient_profiles.id | A |
| 2026-11-25 | No break-glass (emergency) access in the 10-day build | Needs its own review and rules; on the post-demo list | A |
| 2026-11-25 | audit_logs is append-only, has no foreign keys and no updated_at; reads and denials are committed to the log before data is returned | The log must survive and must not be editable; no access without a log row | A |

## Feasibility table (fill on Day 1)
| Service | Works for us? | Works from Syria? | Free limits | Fallback | Date checked |
|---------|---------------|-------------------|-------------|----------|--------------|
| Replit | | | | | |
| Gemini (AI Studio) | | | | | |
| Groq | | | | | |
| OpenRouter | | | | | |
| Hugging Face | | | | | |
| Embedding source | | | | | |
| Neon / Supabase | | | | | |
| GitHub Actions | | | | | |

## Replit credit log
| Date | Balance | Note |
|------|---------|------|
