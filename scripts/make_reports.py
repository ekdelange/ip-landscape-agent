#!/usr/bin/env python
import csv, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_csv(p):
  if not p.exists(): return []
  with p.open(newline="", encoding="utf-8") as f:
    return list(csv.DictReader(f))

def write(p, s):
  p.parent.mkdir(parents=True, exist_ok=True)
  p.write_text(s, encoding="utf-8")

def ip_landscape():
  fm = load_csv(ROOT/"data/processed/family_master.csv")
  ft = load_csv(ROOT/"data/processed/family_tags.csv")
  qa = load_csv(ROOT/"templates/qa_sheet.csv")
  out = ROOT/"deliverables/RF_Plasma_IP_Landscape_v0_9/deck_outline_ip_landscape.md"
  s = f"# RF Plasma IP Landscape — Auto-stitched Draft\n\nGenerated: {datetime.date.today()}\n\n"
  s += f"- Families: {len(fm)}\n- Tags: {len(ft)}\n- QA labels: {len(qa)}\n\n## TODO\n- Insert figures (from BI)\n- Summarize trends & competitor map\n"
  write(out, s)

def sota():
  ev = load_csv(ROOT/"templates/evidence_facts.csv")
  ps = load_csv(ROOT/"templates/product_specs.csv")
  out = ROOT/"deliverables/Plasma_Control_SoTA_v0_9/report_sota.md"
  s = f"# Plasma Control SoTA — Auto-stitched Draft\n\nGenerated: {datetime.date.today()}\n\n"
  s += f"- Evidence facts: {len(ev)} rows\n- Product specs: {len(ps)} rows\n\n## TODO\n- Synthesize per domain\n- Add one-pagers\n"
  write(out, s)

if __name__ == "__main__":
  ip_landscape(); sota(); print("Draft reports generated.")
