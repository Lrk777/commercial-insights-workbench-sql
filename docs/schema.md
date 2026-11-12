# Schema sketch

```text
raw_invoice_lines (invoice line fact, 2024∪2025)
        │
        ▼
stg_invoice_lines  (+ week_start, has_margin_inputs, unit_margin_pct)
        │
        ├── mart_weekly_category
        ├── mart_weekly_county
        └── mart_weekly_vendor
                │
                ├── scorecard_category_wow
                ├── scorecard_county / scorecard_top_stores
                ├── margin_coverage
                ├── vendor_concentration
                └── wow_anomaly_flags
```

**Primary business grain attempted:** `invoice_id` (DQ shows it is **not** unique in this extract — document before reconciling).  
**Analytics grains used:** week × category · week × county · vendor · store.
