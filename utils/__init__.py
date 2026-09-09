"""QA Defects Dashboard — shared utilities.

Modules:
- real_supply: derived OTIF/SCAR/PPM from defect log + supplier master (proxies,
  not real delivery tracking — see disclaimer banner in app.py)
- mock_supply: legacy mock data kept for fallback / tests; do NOT import in prod
  pages (grep audit: random.seed in production = silent correctness trap)
- supplier_aliases: alias map reconciling "NISSEN CHEMITEC" (defect log) vs
  "NISSEN" (supplier_master) vs "NISSEN CHEMITEC" (templates)
- validation: validate_dataframe() shared between load_data() and the Excel
  upload handler
"""
