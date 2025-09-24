# IP Data Agent — A1–A4

## A1 Ontology → `queries/ontology.json`
Keys:
- domains: ["RF Generator","Matching Network","Vacuum Capacitor","Firmware/Control","Sensors","Reliability/EMC/Thermal"]
- synonyms: per-domain list (e.g., RF Generator → ["RF power supply","RF amplifier","class E","LDMOS","GaN"])
- negative_terms: e.g., {"RF Generator":["microwave oven","medical diathermy"]}
- assignee_aliases: canonical → variants (e.g., "COMET":["Comet AG","COMET PCT","Comet Plasma Control Technologies"])
- geos: ["US","EP","JP","KR","CN","TW"]
- years: {"from":2005,"to":<current-year>}
Also write `queries/glossary.md`.

## A2 Query library → `queries/query_library.csv`
Columns: topic,engine,query,notes
- Provide 8–12 Boolean queries per domain for **Google Patents** and **Espacenet**.
- Use both keyword and CPC/IPC filters (H05H, H02M, H03F, H01G/H01T, C23C).
- Example:
RF Generator,google,"(\"RF generator\" OR \"RF power supply\") AND (plasma OR etch OR CVD) AND (13.56 OR 27.12 OR 40.68 OR 60) AND (GaN OR LDMOS)","keyword+freq anchors"

## A3 Pipeline spec → `runbooks/pipeline_spec.md`
Describe ingest of CSV exports → clean → INPADOC family group → assignee normalize → domain tag (rules).

## A4 QA → `templates/qa_sheet.csv`
Label ≥50 docs; summarize precision/recall and suggested query fixes.
