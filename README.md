# Comet PCT — RF Plasma Control Research Pack (v0.1)

This workspace bootstraps the two research packs you need *before* drafting a mandate:
1) **RF Plasma IP Landscape (v0.9)** — reproducible queries, family-level analytics, competitor positioning.
2) **Plasma Control SoTA (v0.9)** — evidence-based view across RF generators, matching networks, vacuum capacitors, control/sensors.

Open `runbooks/how_to_run_agents.md` to start.

## Quickstart
1) Open this folder in VS Code → accept recommended extensions.
2) (Optional) Python venv:
   - Windows PowerShell
     ```
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     pip install -r requirements.txt
     ```
   - macOS/Linux
     ```
     python3 -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt
     ```
3) Follow `runbooks/sprint_plan.md` and use prompts in `/prompts` in order.
4) Drop patent exports into `/data/raw/`, then run **Tasks → Validate data tables**.

## Structure
.
├─ .vscode/  (tasks, extensions, settings)
├─ CASE_SUMMARY.md
├─ prompts/  (orchestrator + agents)
├─ queries/  (ontology, glossary, query_library.csv)
├─ schemas/  (JSON schemas)
├─ templates/ (CSV & MD templates, Mermaid maps, DAX)
├─ scripts/  (validate.py, make_reports.py)
├─ runbooks/ (sprint plan, checklist, agent setup, logs)
├─ data/{raw|interim|processed}
├─ deliverables/{RF_Plasma_IP_Landscape_v0_9,Plasma_Control_SoTA_v0_9}
└─ requirements.txt
