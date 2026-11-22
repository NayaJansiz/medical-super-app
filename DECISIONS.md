# Decisions log

| Date | Decision | Why | Who |
|------|----------|-----|-----|
| 2026-11-22 | Trunk-based Git, no develop branch | 2 people, 10 days | both |
| 2026-11-22 | Python/FastAPI backend, React/TypeScript frontend | AI, RAG, OCR and CSV import are the hardest modules and Python's ecosystem is strongest there. Pydantic gives built-in validation. Cost: two languages. | both |
| 2026-11-22 | AGENTS.md in repo is the source of truth for AI instructions | Free Claude Projects are not shared; ChatGPT, Gemini and Replit cannot see them | both |
| 2026-11-22 | uv with lock file | Identical environments on both machines | both |

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
