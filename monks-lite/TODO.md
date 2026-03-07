# Monks Biweekly Lite — TODO 📋

> Dashboard: `afterpay-monks-lite.html` (v2.0)
> Backend engine: `../backend/engines/monks_biweekly.py`
> API endpoint: `/api/monks-biweekly`

---

## ✅ What's Done

- [x] v2.0 dashboard — Executive Summary, Channel Temp-Check, Spend Allocation Donut, Regional Breakdown, Heatmap, Watch-Outs & Action Items
- [x] Backend engine with channel × region queries, 7 alert rules, executive summary generation
- [x] API endpoint serving Monks dashboard payload

---

## 🔴 TODO

- [ ] **Data automation** — Currently manual .xlsx handoff every 2 weeks
  - If Monks can drop files to a shared location (GDrive, S3, Snowflake stage), we can automate ingestion
- [ ] **Rebuild as v3.0** — Rebuild with the same v3.0 design system used in the B2B dashboard
- [ ] **Ask IT/security about external sharing** — Can agency vendors (Monks) access Blockcell directly?

---

*Last updated: March 7, 2026 — v2.0 live, manual data refresh. TODO split out from B2B during repo reorganization.*
