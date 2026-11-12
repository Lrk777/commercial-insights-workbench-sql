# Interview talk-track (60 seconds)

On a junior commercial insights / BI seat I’d own the weekly **certify → scorecard → memo** loop.

In this public workbench I used Iowa Class-E invoice data as a warehouse stand-in: DuckDB load, DQ exception report, metric dictionary, weekly category/county marts, WoW variance, vendor concentration, and a stakeholder memo.

The important judgment call: **margin fields were missing on most rows**, so the SQL marks categories `do_not_report_margin` instead of inventing a KPI. That’s the same discipline I’d bring to Bimbo-style RGM or Allstate-style BI work — trust the data before the story.
