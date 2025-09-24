## IP Data Pipeline Specification

Owner: IP Data Agent  
Version: 0.1 (draft)  
Scope: Transform heterogeneous patent publication exports (Google Patents, Espacenet) into normalized family-level datasets with ontology-based tagging.

---
### 1. Overview
Raw patent publication CSV exports are ingested from `/data/raw/`. The pipeline harmonizes schema, cleans & normalizes textual / date fields, groups publications into INPADOC families, applies assignee alias resolution, derives domain tags using the ontology, and emits curated intermediate and processed tables.

High-level stages:
1. Ingest & Identify Source Schema
2. Column Mapping & Cleaning
3. Normalization (text, dates, assignees)
4. Family Grouping (INPADOC based)
5. Tagging (rules-based multi-label)
6. Output Generation (interim + processed)

---
### 2. Inputs
Location: `/data/raw/*.csv`

Two primary source types with typical column sets (actual export names may vary):

Google Patents export (example columns):
- `publication_number`
- `family_id` (INPADOC or Google cluster id; prefer INPADOC if present)
- `priority_date` / `filing_date`
- `publication_date`
- `title`
- `abstract`
- `assignee` (may be semi-colon separated list)
- `inventor`
- `cpc` (pipe or semicolon separated codes)
- `ipc`
- `application_number`
- `country_code`
- `kind_code`
- `claims`
- `description`

Espacenet export (example columns):
- `pn` (publication number)
- `inpadoc_family_id`
- `prio_date`
- `pub_date`
- `app_date`
- `title_en`
- `abstract_en`
- `applicant` / `assignee`
- `inventor`
- `cpc_codes`
- `ipc_codes`
- `claims_text`
- `description_text`

Mandatory minimal fields required for inclusion downstream:
- Publication Identifier (normalized `pub_id`)
- Family Identifier (temporary if missing; later replaced by INPADOC family) 
- At least one of: `title`, `abstract`
- `publication_date` (parsable)

---
### 3. Cleaning & Column Rename
Objective: unify into a standard interim schema (publication-level) => `patent_raw`.

Standard column target names:
- `pub_id` (from `publication_number` | `pn`)
- `family_id_src` (from `family_id` | `inpadoc_family_id` | NULL)
- `priority_date` (ISO date) (from `priority_date` | `prio_date`)
- `filing_date` (from `filing_date` | `app_date`)
- `publication_date` (from `publication_date` | `pub_date`)
- `title` (`title` | `title_en`)
- `abstract` (`abstract` | `abstract_en`)
- `assignees_raw` (`assignee` | `applicant`)
- `inventors_raw`
- `cpc_raw`
- `ipc_raw`
- `claims_raw`
- `description_raw`
- `source` (enum: `google`, `espacenet`)
- `ingest_filename`
- `ingest_ts` (UTC timestamp of load)

Steps:
1. Read CSV with UTF-8; strip BOM.
2. Trim whitespace on all string cells.
3. Normalize column headers to lower snake_case before mapping.
4. Apply mapping dict per source; drop unmapped extraneous columns (retain for audit only if needed).
5. Ensure date fields: try parse (YYYY-MM-DD preferred). Accept fallback patterns: `YYYY/MM/DD`, `DD-MMM-YYYY`. If parse fails, set NULL and log warning.
6. Deduplicate identical rows (hash of all canonical columns) keeping earliest ingest.

Text normalization:
- Collapse repeated whitespace to single space in `title`, `abstract`.
- Remove control characters.
- Lowercase copy kept only for tagging (do not overwrite original case fields for output readability).

---
### 4. Family Grouping
Rule priority:
1. If `family_id_src` present and numeric (INPADOC), use as `family_id`.
2. Else construct temporary family key by concatenating sorted unique priority dates + first applicant hashed (stable SHA1 truncated 12 chars) => `tempfam_<hash>`.
3. After optional enrichment (future), replace temp IDs when authoritative INPADOC mapping becomes available.

Family canonical attributes (computed at grouping stage):
- `family_id` (final as above)
- `earliest_priority_date` (min of non-null `priority_date` across family)
- `earliest_filing_date`
- `earliest_publication_date`
- `member_count` (# of publications)
- `representative_pub_id` (choose publication with earliest priority; tiebreaker: earliest publication_date; else lexical smallest pub_id)

---
### 5. Assignee Normalization
Assignee alias mapping source: ontology / configuration (e.g., `assignee_aliases` in `queries/ontology.json`).

Procedure:
1. Split `assignees_raw` on `;|,` boundaries; trim tokens.
2. Lowercase & remove punctuation for matching (keep original for audit).
3. For each token, if matches alias list (exact after normalization) assign canonical `assignee_std`.
4. If multiple canonical values map within a publication, retain all (pipe separated) but deduplicate.
5. Provide additional derived field `assignee_std_primary` = first canonical (alphabetically) or NULL.

---
### 6. Tagging (Ontology-based Domain Assignment)
Domains from `queries/ontology.json: domains[]` with synonyms lists.

Matching windows: combine `title` + `abstract` (lowercased) into `text_window`.

Per domain D:
1. Build keyword set = domain label + synonyms.
2. Simple token / phrase match (case-insensitive, whole phrase). Allow stemming via wildcard suffix match for patterns containing spaces? (Out of scope: initial version plain substring, bounded by word boundaries where feasible).
3. If any keyword hits, assign tag D.
4. Multi-tag allowed; store as pipe-delimited in `domain_tags` (order = sorting by domain name for determinism).

Negative terms: If domain has configured `negative_terms` and any appear in `text_window`, still keep match but log for manual review (initial iteration does not auto-exclude to avoid false negatives).

Intermediate tagging table (publication-level) includes:
- `pub_id`, `domain_tags`.

Family tag aggregation:
For each family: union of all member `domain_tags`; store pipe-delimited sorted unique set.

---
### 7. Outputs

1. Interim publication-level unified dataset: `/data/interim/patent_raw.csv`
	- Contains cleaned & normalized publication rows (schema below).
2. Processed family master: `/data/processed/family_master.csv`
	- One row per family with canonical dates & representative publication.
3. Processed family tags: `/data/processed/family_tags.csv`
	- Multi-label domain tags per family (exploded optional in analytics layer).

---
### 8. Data Contracts (Schemas)

`patent_raw.csv` (publication-level)
| Column | Type | Description |
|--------|------|-------------|
| pub_id | string | Normalized publication number (no spaces) |
| family_id_src | string? | Source-provided family id (may be INPADOC) |
| family_id | string | Final family id (after grouping) |
| priority_date | date? | Earliest claimed priority of this publication |
| filing_date | date? | Application filing date |
| publication_date | date | Publication date (required if available) |
| title | string | Title (original casing) |
| abstract | string? | Abstract (may be null) |
| assignees_raw | string? | Raw assignee string prior to normalization |
| assignee_std | string? | Pipe-delimited normalized assignees |
| assignee_std_primary | string? | Primary normalized assignee |
| inventors_raw | string? | Raw inventor listing |
| cpc_raw | string? | Raw CPC codes list |
| ipc_raw | string? | Raw IPC codes list |
| claims_raw | string? | Raw claims text or truncated snippet |
| description_raw | string? | Raw description text or snippet |
| domain_tags | string? | Pipe-delimited domain tags (publication-level) |
| source | enum | `google` or `espacenet` |
| ingest_filename | string | Source filename |
| ingest_ts | timestamp | Ingest UTC timestamp |

`family_master.csv`
| Column | Type | Description |
|--------|------|-------------|
| family_id | string | Final family id |
| representative_pub_id | string | Selected representative publication |
| earliest_priority_date | date? | Min priority date across family |
| earliest_filing_date | date? | Min filing date |
| earliest_publication_date | date? | Min publication date |
| member_count | integer | Number of member publications |
| family_assignees | string? | Pipe-delimited union of normalized assignees |
| family_domains | string? | Pipe-delimited union of domain tags |

`family_tags.csv`
| Column | Type | Description |
|--------|------|-------------|
| family_id | string | Family id |
| domain | string | Single domain label |

---
### 9. Minimal Examples (Headers Only)
Below are header-only CSV examples (no data rows) to clarify ordering.

`/data/interim/patent_raw.csv`
```
pub_id,family_id_src,family_id,priority_date,filing_date,publication_date,title,abstract,assignees_raw,assignee_std,assignee_std_primary,inventors_raw,cpc_raw,ipc_raw,claims_raw,description_raw,domain_tags,source,ingest_filename,ingest_ts
```

`/data/processed/family_master.csv`
```
family_id,representative_pub_id,earliest_priority_date,earliest_filing_date,earliest_publication_date,member_count,family_assignees,family_domains
```

`/data/processed/family_tags.csv`
```
family_id,domain
```

---
### 10. Notes & Assumptions
- No external API calls assumed for INPADOC enrichment beyond provided exports (future extension: OPS or Google bulk). 
- Text fields may be truncated upstream; pipeline preserves as-is aside from whitespace normalization.
- Timezone for dates assumed UTC (date-only semantics). Timestamps recorded in ISO 8601 with `Z`.
- Multi-language abstracts not handled in v0.1 (English assumed if multiple, choose first English field encountered).

### 11. Future Enhancements (Out of Scope Now)
- Semantic tagging (ML classifier) to complement keyword ontology.
- Automated negative-term exclusion logic with precision tracking.
- Family legal status enrichment & grant filtering.
- Deduplication of near-duplicate abstracts (shingling / simhash).

END
