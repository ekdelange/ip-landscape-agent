# Orchestrator Agent — Plan & Checkpoints

**Goal:** Coordinate 6 specialized agents to produce two research packs:
1) RF Plasma IP Landscape (v0.9)
2) Plasma Control SoTA (v0.9)

**Execution Order:** Phase A (A1→A6) then Phase B (B1→B6). Halt after each Acceptance Criterion (AC), perform validations, log checkpoint, then continue.

## Agents
- IP Data Agent (A1–A4 data foundations)
- Patent Analytics Agent (A5 insights + figures)
- Literature Agent (B2–B3 evidence ingestion)
- Competitor Products Agent (B4 product specs + metric ranges)
- Synthesis Agent (B5 narrative + hypotheses)
- Red-Team Agent (continuous QA; formal review after each AC)

## Phase Breakdown
| Phase | Step | Agent | Output | Depends On |
|-------|------|-------|--------|------------|
| A | A1 | IP Data | `queries/ontology.json` + `queries/glossary.md` | — |
| A | A2 | IP Data | `queries/query_library.csv` | A1 |
| A | A3 | IP Data | `runbooks/pipeline_spec.md` | A2 |
| A | A4 | IP Data | `templates/qa_sheet.csv` (≥50 labels) | A3 |
| A | A5 | Patent Analytics | `deliverables/RF_Plasma_IP_Landscape_v0_9/deck_outline_ip_landscape.md` + figures | A4 (and processed data) |
| A | A6 | Red-Team | Interim QA notes in `runbooks/red_team_findings.md` | A5 |
| B | B1 | (Transition) | Ensure Phase A artifacts frozen (tag in log) | A6 |
| B | B2 | Literature | `queries/lit_seed.csv` | B1 |
| B | B3 | Literature | `templates/evidence_facts.csv` + schema confirm | B2 |
| B | B4 | Competitor Products | `templates/product_specs.csv` + `templates/sota_matrix.csv` | B3 |
| B | B5 | Synthesis | `deliverables/Plasma_Control_SoTA_v0_9/report_sota.md` + one_pagers | B4 |
| B | B6 | Red-Team | Final QA + `runbooks/red_team_findings.md` updates | B5 |

## Acceptance Criteria (AC)
| # | Files / Artifacts | Validation Summary | Pass Conditions |
|---|-------------------|--------------------|----------------|
| 1 | `queries/ontology.json`, `queries/glossary.md` | JSON parses; glossary ≥ 1 term per ontology domain | No empty domain lists; year range valid |
| 2 | `queries/query_library.csv` | CSV parses; ≥8 queries/domain; engines include google & espacenet | No duplicate identical query strings per domain/engine |
| 3 | `runbooks/pipeline_spec.md` | Contains stages ingest→clean→family_group→normalize→tag | Each stage has inputs, outputs, tools |
| 4 | `templates/qa_sheet.csv` | ≥50 labeled docs; columns include label & rationale | Precision/recall commentary present |
| 5 | `deck_outline_ip_landscape.md` | All required sections populated; figures referenced exist | ≥5 hypotheses, momentum & whitespace sections present |
| 6 | `queries/lit_seed.csv` | Per-domain seeds ≥8 rows; required columns present | No missing abstracts unless TODO flagged |
| 7 | `templates/evidence_facts.csv` | Schema fields align; ≥1 metric/domain | Units populated for quantitative metrics |
| 8 | `templates/product_specs.csv` | Required columns present; ≥10 products overall | Confidence field populated per row |
| 9 | `report_sota.md` | Domains covered; frontiers + hypotheses + risks | Each opportunity tied to evidence/product gaps |

## Global Rules
- Save artifacts exactly at specified paths (case-sensitive where applicable).
- After each AC: append a 5-line checkpoint to `runbooks/execution_log.md` (format below).
- If uncertain: insert `TODO:` inline (max 120 chars) and proceed. Red-Team will triage.
- Never overwrite prior evidence; append new rows (idempotent updates require dedupe keys defined below).

## Checkpoint Log Format (5 lines)
```
AC<n>: <artifact summary> | status=PASS|FAIL|PARTIAL
Stats: <counts/rows/figures>
Risks: <top 1 risk or NONE>
Next: <next step id>
Timestamp: <UTC ISO8601>
```
If FAIL: add a 6th line `Remediate: <planned fix>`.

## Dedupe / Idempotency Keys
- evidence_facts.csv: (source_id, metric, domain)
- product_specs.csv: (vendor, product)
- lit_seed.csv: (DOI_or_URL)
- qa_sheet.csv: (doc_id) — doc_id derived from patent/publication identifier

## Validation Hooks (pseudo)
```
for ac in 1..9:
	run local validator (scripts/validate.py) subset
	if pass -> log PASS
	elif minor gaps (only TODO items) -> log PARTIAL and continue
	else -> log FAIL and create TODO in execution_log, continue only if non-blocking
```

## Error Recovery
1. Detect malformed file (parse error) → restore last good version from git + record TODO.
2. Missing required column → append column with placeholder `TODO_missing` values.
3. Insufficient row count → proceed; flag as PARTIAL; prioritize enrichment before downstream dependency that needs density.
4. Broken figure reference → insert placeholder text `FIGURE_TBD:<id>`.

## Red-Team Integration
- After each AC: quick scan for unsubstantiated claims & data integrity.
- At AC5 & AC9: perform deep traceability audit (claim→row/paper).
- Findings appended to `runbooks/red_team_findings.md` and summarized in checkpoint risk line.

## TODO Conventions
`TODO:gap_type: concise note` (e.g., `TODO:data: need CPC filter refinement for matching networks`).
Gap types: data, query, metric, figure, hypothesis, validation.

## Execution Commands (examples)
Validation subset:
`python scripts/validate.py --ac 1` (extend script to accept `--ac` arg; fallback: manual inspection).
Build draft reports:
`python scripts/make_reports.py` (ensures deck/report compiled once prerequisites exist).

## Completion Definition
All 9 ACs status PASS (or PARTIAL only for non-critical aesthetic gaps), red-team high-risk items resolved or accepted.

## Initial Start Procedure
1. Run ontology (A1) creation.
2. Immediately validate JSON structure.
3. Proceed through phases using table above.

## Notes
- Keep narrative artifacts (deck/report) lean until underlying datasets stabilize (freeze after A6 and B6 respectively).
- Prefer reproducible transformations captured in pipeline spec over ad-hoc edits.

## (Original Minimal Checklist Retained Below for Reference)
1. `queries/ontology.json` + `queries/glossary.md`
2. `queries/query_library.csv`
3. `runbooks/pipeline_spec.md`
4. `templates/qa_sheet.csv` (≥50 labels)
5. `deliverables/RF_Plasma_IP_Landscape_v0_9/deck_outline_ip_landscape.md` (filled)
6. `queries/lit_seed.csv`
7. `templates/evidence_facts.csv` (filled)
8. `templates/product_specs.csv` (filled)
9. `deliverables/Plasma_Control_SoTA_v0_9/report_sota.md` (filled)
