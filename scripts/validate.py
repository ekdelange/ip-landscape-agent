#!/usr/bin/env python
import csv, json, argparse, sys, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
  "family_master": ROOT/"schemas/family_master.schema.json",
  "family_tags": ROOT/"schemas/family_tags.schema.json",
  "product_specs": ROOT/"schemas/product_specs.schema.json",
  "evidence_facts": ROOT/"schemas/evidence_facts.schema.json",
  "sota_matrix": ROOT/"schemas/sota_matrix.schema.json"
}
TABLES = {
  "family_master": ROOT/"templates/family_master.csv",
  "family_tags": ROOT/"templates/family_tags.csv",
  "product_specs": ROOT/"templates/product_specs.csv",
  "evidence_facts": ROOT/"templates/evidence_facts.csv",
  "sota_matrix": ROOT/"templates/sota_matrix.csv"
}
def read_schema(p): return json.loads(p.read_text(encoding="utf-8"))
def read_headers(p):
  with p.open(newline="", encoding="utf-8") as f:
    return next(csv.reader(f))
def validate_all_tables():
  for name in TABLES:
    sch = read_schema(SCHEMAS[name])
    req = sch.get("required", [])
    props = list(sch.get("properties", {}).keys())
    headers = read_headers(TABLES[name])
    missing = [r for r in req if r not in headers]
    extra = [h for h in headers if h not in props]
    if missing or extra:
      print(f"[{name}] missing={missing} extra={extra}")
    else:
      print(f"[{name}] headers OK")

def ac1():
  ont = ROOT/"queries/ontology.json"
  gloss = ROOT/"queries/glossary.md"
  if not ont.exists():
    return False, "ontology.json missing"
  try:
    data = json.loads(ont.read_text(encoding="utf-8"))
  except Exception as e:
    return False, f"ontology.json parse error: {e}" 
  domains = data.get("domains", [])
  years = data.get("years", {})
  ok = bool(domains) and years.get("from",0) < years.get("to",0)
  gloss_ok = gloss.exists() and gloss.read_text(encoding="utf-8").strip() != ""
  return ok and gloss_ok, f"domains={len(domains)} gloss={'ok' if gloss_ok else 'missing'}"

def ac2():
  path = ROOT/"queries/query_library.csv"
  if not path.exists():
    return False, "query_library.csv missing"
  with path.open(newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
  by_domain = {}
  for r in rows:
    d = r.get('topic','').strip()
    by_domain.setdefault(d, set()).add((r.get('engine',''), r.get('query','')))
  sufficient = all(len(v) >= 8 for v in by_domain.values()) and len(by_domain) >= 1
  return sufficient, f"domains={len(by_domain)} min_queries={min((len(v) for v in by_domain.values()), default=0)} total_rows={len(rows)}"

def ac3():
  p = ROOT/"runbooks/pipeline_spec.md"
  if not p.exists(): return False, "pipeline_spec.md missing"
  txt = p.read_text(encoding='utf-8').lower()
  needed = ["ingest","clean","family","normalize","tag"]
  missing = [k for k in needed if k not in txt]
  return not missing, f"missing_sections={missing}" if missing else "sections_ok"

def ac4():
  p = ROOT/"templates/qa_sheet.csv"
  if not p.exists(): return False, "qa_sheet.csv missing"
  with p.open(newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
  cols = rows[0].keys() if rows else []
  return (len(rows) >= 50 and 'label' in cols), f"rows={len(rows)} cols={len(cols)}"

def ac5():
  p = ROOT/"deliverables/RF_Plasma_IP_Landscape_v0_9/deck_outline_ip_landscape.md"
  if not p.exists(): return False, "deck_outline_ip_landscape.md missing"
  txt = p.read_text(encoding='utf-8').lower()
  needed = ["hypotheses","momentum","white-space"]
  missing = [k for k in needed if k not in txt]
  return not missing, f"missing={missing}" if missing else "sections_ok"

def ac6():
  p = ROOT/"queries/lit_seed.csv"
  if not p.exists(): return False, "lit_seed.csv missing"
  with p.open(newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
  domains = {}
  for r in rows:
    domains.setdefault(r.get('domain','').strip(), 0)
    domains[r.get('domain','').strip()] += 1
  enough = rows and all(c >= 8 for c in domains.values())
  return enough, f"domains={len(domains)} min_rows_domain={min(domains.values()) if domains else 0} total_rows={len(rows)}"

def ac7():
  p = ROOT/"templates/evidence_facts.csv"
  if not p.exists(): return False, "evidence_facts.csv missing"
  with p.open(newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
  metrics = {r.get('metric','') for r in rows}
  domains = {r.get('domain','') for r in rows}
  return (len(rows) >= len(domains)), f"rows={len(rows)} metrics={len(metrics)} domains={len(domains)}"

def ac8():
  p = ROOT/"templates/product_specs.csv"
  if not p.exists(): return False, "product_specs.csv missing"
  with p.open(newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
  cols = rows[0].keys() if rows else []
  required = {"vendor","product","confidence"}
  missing = required - set(cols)
  return (len(rows) >= 10 and not missing), f"rows={len(rows)} missing_cols={list(missing)}"

def ac9():
  p = ROOT/"deliverables/Plasma_Control_SoTA_v0_9/report_sota.md"
  if not p.exists(): return False, "report_sota.md missing"
  txt = p.read_text(encoding='utf-8').lower()
  needed = ["frontier","hypotheses","risk"]
  missing = [k for k in needed if k not in txt]
  return not missing, f"missing={missing}" if missing else "sections_ok"

AC_FUNCS = {1: ac1,2: ac2,3: ac3,4: ac4,5: ac5,6: ac6,7: ac7,8: ac8,9: ac9}

def main():
  parser = argparse.ArgumentParser(description="Validation utility for IP landscape pipeline")
  parser.add_argument('--ac', type=int, help='Run only a specific acceptance criterion check (1-9)')
  args = parser.parse_args()
  if args.ac:
    fn = AC_FUNCS.get(args.ac)
    if not fn:
      print("Invalid AC number", file=sys.stderr); sys.exit(2)
    ok, detail = fn()
    status = 'PASS' if ok else 'FAIL'
    print(f"AC{args.ac} {status} {detail}")
    sys.exit(0 if ok else 1)
  # Default: legacy full table header validation + all AC summary
  validate_all_tables()
  for n, fn in AC_FUNCS.items():
    ok, detail = fn()
    print(f"AC{n}: {'PASS' if ok else 'FAIL'} {detail}")
  print("Validation completed.")

if __name__ == '__main__':
  main()
