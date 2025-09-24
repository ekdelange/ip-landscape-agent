# Literature Agent — B2–B3

## B2 Source triage → `queries/lit_seed.csv`
Columns: domain,query,title,venue,year,DOI_or_URL,abstract,evidence_level  
Provide ~10 per domain (RF gen, match, vac caps, control/sensors). Favor quantitative benchmarks (IEEE/AVS/PELS).

## B3 Evidence extraction
1) Schema → `schemas/evidence_facts.schema.json` (fields+units)  
2) Facts table → `templates/evidence_facts.csv`  
Row: source_id,domain,metric,value,units,conditions,citation,evidence_level
