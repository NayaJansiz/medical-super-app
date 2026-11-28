## Plan item
<!-- The PLAN.md line this closes, e.g. "Sat 28 Nov: invoices". Tick the box in this PR. -->

## What and why

## How to test
<!-- Exact steps or the test names. Screenshots for UI changes (include Arabic). -->

## Risk
- [ ] Security-sensitive (auth, consent, audit, AI safety, security code, migrations, CI): **the other engineer must approve before merge**
- [ ] Routine: self-merge on green CI

## Checklist
- [ ] `make check` passes locally; CI is green
- [ ] Authorization checked: who may call this, and what may they see?
- [ ] Tests include happy path, validation failure, and every role against every endpoint
- [ ] Migration reviewed by hand; `make migrate` works
- [ ] No secrets, no patient data in logs, fake data has `is_synthetic = true`
- [ ] Medical content without a verified source is labelled "unverified"
- [ ] PLAN.md ticked; DECISIONS.md / SCHEMA.md updated if relevant

## AI use
<!-- Which tool wrote it, which different tool reviewed it. -->
