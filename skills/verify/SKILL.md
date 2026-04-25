---
name: verify
description: "Check resume for fabrication and provenance integrity. Use when: 'verify resume', 'check claims', 'anti-fabrication check', 'audit resume'."
---

# /verify — Anti-Fabrication Verification

## Purpose
Verify that all claims in resume.yaml trace back to source artifacts and no fabrication has occurred.

## Process

1. Run `resume-builder verify --resume resume.yaml` for deterministic provenance check
2. Review each bullet for:
   - **Fabricated claims**: metrics, technologies, or experiences not backed by provenance
   - **Overclaiming**: embellished scope, inflated metrics, solo credit for team work
   - **Verb discipline**: "led" vs "contributed to", "architected" vs "worked on"
   - **Metric accuracy**: do the numbers match what provenance artifacts show?
3. Check corrections.yaml for previously caught errors — flag if reintroduced
4. Report findings with severity levels:
   - **ERROR**: Fabricated metric, company, or technology
   - **WARNING**: Meaning changed through rephrasing
   - **INFO**: Minor rewording, acceptable

## Output
```
## Verification Report

### Status: PASS / FAIL

### Errors (must fix)
- ...

### Warnings (review recommended)
- ...

### Info (acceptable)
- ...

### Provenance Coverage
- X/Y bullets have provenance
- X/Y bullets are verified
- X/Y projects have artifact links
```
