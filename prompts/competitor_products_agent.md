# Competitor Products Agent — B4

Outputs:
- `templates/product_specs.csv` (one product/row)
- `templates/sota_matrix.csv` (metric dictionary & typical ranges)

product_specs fields:
vendor,product,domain,power_W,freq_MHz,efficiency_pct,tuning_time_ms,cooling,interfaces,actuation,algorithm,footprint,notes,confidence

Record "as-advertised" specs; mark confidence as `datasheet` vs `independent`.
