# Afterpay B2B Dashboard — Master To-Do 📋

> **This file is the single source of truth.** Start every new Goose session by reading this file instead of searching chat history. It replaces all prior conversation context.
>
> **Session startup prompt:** *"Read /Users/npetrillo/repos/block/b2b-dg-dashboard/TODO.md — it has everything you need. Don't search chat history."*

---

## 🏗️ Project Overview

Afterpay B2B Demand Gen Dashboard + shared Python backend, built by Nick Petrillo with Goose 🪿.

| Asset | File | Status |
|---|---|---|
| B2B Demand Gen Dashboard v3.0 | `afterpay-b2b-demand-gen-v3.html` | ✅ Complete (2,129 lines) |
| Python Backend (shared) | `../backend/` | ✅ Built, needs Snowflake creds to go live |
| Blockcell (hosted) | https://blockcell.sqprod.co/sites/afterpay-b2b-demand-gen/ | ✅ v3.0 live (w/ sparklines) |
| GitHub | https://github.com/npetrillo-block/block.git | ✅ `main` branch |

---

## ✅ What's Done

### v3.0 Dashboard (afterpay-b2b-demand-gen-v3.html)
- [x] Full CSS design system (dark/light themes, 30+ component classes, responsive breakpoints)
- [x] Header: gradient title, Live badge with pulsing dot, theme toggle (💡), 4 filter pills
- [x] 5 main tab pills (Overview, Channels, Lead Sources, Funnel, Trends)
- [x] JS: tab switching, theme toggle (localStorage + auto-detect 9am-5pm), IntersectionObserver
- [x] **Overview tab** (7 sections):
  - KPI Summary (6 cards: Leads, MQLs, MQL Rate, Open Opps, Merchants Won, Conv Rate)
  - Insights at a Glance (6 wins + 6 watchouts)
  - Lead Volume by Channel (canvas bar chart + detailed breakdown table)
  - Channel Deep Dive (5 inner tabs × 4-6 seg-metric cards with mini-bars)
  - Channel Performance Summary All-Time (compact table)
  - SEM Regional Breakdown (US/AU/UK/NZ × Branded/Non-Brand/Competitor/PMax)
  - vs. Target placeholder (dashed border, waiting for targets data)
- [x] **Channels tab** (5 channel cards with colored top borders):
  - SEM (#4ecdc4): Branded/PMax/Non-Brand/Competitor mini-grid
  - Paid Social (#a78bfa): Meta + LinkedIn sub-cards, insight callout
  - Programmatic (#fbbf24): DV360 note
  - ABM (#f472b6): 6sense + Demandbase
  - Non-Paid (#60a5fa): Direct/Unknown/Organic, insight callout
- [x] **Lead Sources tab**:
  - 9 source cards (Self-Serve, Contact Us, Historical, Prospecting, Brand Expansion, Content, Partner, Physical Event, 1:1 Merchant Intro)
  - Conversion Rate by Source canvas bar chart (sorted desc)
- [x] **Funnel tab**:
  - Vertical pipeline (Prospect → MQL → SQL → Open Opp → Merchant Won)
  - Exit Paths (Disqualified, Closed Lost, Nurture, Unknown)
  - Insight callout (Open Opps > MQL+SQL because Self-Serve bypasses)
  - Post-Conversion Journey (Get Transacting → Adopt → Boost → Retain)
- [x] **Trends tab**:
  - Monthly Leads & MQLs (bars + line, 14 months)
  - Monthly Merchants Won (green-to-red gradient bars)
  - Channel Mix Over Time (stacked bars)
  - 3 trend insight callouts
- [x] 5 canvas chart functions (retina, theme-aware, resize-debounced)
- [x] Footer: "(v3.0) Live Dashboard — Powered by Snowflake · Made with ❤️ by Nick and Goose 🪿"

### Python Backend (backend/)
- [x] `config.py` — env vars, Snowflake creds (TODO placeholders), alert thresholds
- [x] `snowflake_connector.py` — SnowflakeClient class, context manager
- [x] `server.py` — FastAPI with 6 endpoints, CORS, 1hr cache
- [x] `scheduler.py` — APScheduler daily job at 7 AM, uvicorn launcher
- [x] `engines/b2b_demand_gen.py` — SQL template, fallback data, YoY calcs
- [x] `engines/monks_biweekly.py` — channel × region queries, 7 alert rules
- [x] `engines/insight_engine.py` — formatting + narrative generation
- [x] `notifications/slack_notifier.py` — Block Kit alerts, summaries, staleness warnings
- [x] `notifications/email_notifier.py` — HTML digest, staleness warnings
- [x] `env.example` — template with all config vars documented

### Data Discovery (completed)
- [x] Confirmed primary table: `FIVETRAN.MARKETO.LEAD` (11.3M rows)
- [x] Filter: `AFTERPAY_BU = 'Afterpay'` → ~198K leads
- [x] Channel logic: `LAST_TOUCH_UTM_MEDIUM_C` → cpc/p-social/disp/else
- [x] Funnel column: `PROSPECT_LIFECYCLE_STATUS_C`
- [x] Post-conversion: `MARKETO_LIFECYCLE_STAGE` (Get Transacting/Adopt/Boost/Retain)
- [x] Lead source: `LEAD_SOURCE_CHANNEL_C` (Self-Serve, Contact Us, etc.)
- [x] Identified upstream table: `AP_MER_ANALYTICS.BETA.SMB_LEADS` (richer, needs access)
- [x] Sophia Liu's team owned the pipeline (she was laid off — need to find new owner)

---

## 🔴 To-Do — Priority Order

### P0: Immediate (Do Next Session)

- [x] **Deploy v3.0 to Blockcell** — ✅ Deployed Mar 7, 2026 (version `XLaQYQKmaElsKOrArJyzMZhwwy7_cGSF`)
  - URL: https://blockcell.sqprod.co/sites/afterpay-b2b-demand-gen/

### P1: Slack Integration (2 minutes once webhook exists)

- [ ] **Create Slack incoming webhook**
  - Go to Slack admin → Apps → Incoming Webhooks → Create for your channel
  - Paste URL into `backend/.env` as `SLACK_WEBHOOK_URL`
- [ ] **Test Slack alerts** — Run `python scheduler.py --once` to verify alerts fire
- [ ] **Configure alert thresholds** — Review/tune thresholds in `backend/config.py`

### P2: Snowflake Live Connection (the big unlock)

- [ ] **Get Snowflake service account credentials**
  - Need: account ID, username, password, warehouse name
  - Ask whoever inherited Sophia Liu's team (Commerce GTM DS)
  - Request: "Read-only service account with SELECT access to `FIVETRAN.MARKETO.LEAD`"
  - Bonus: also request access to `AP_MER_ANALYTICS.BETA.SMB_LEADS` (richer data)
- [ ] **Configure .env** — Fill in Snowflake creds from `env.example` template
- [ ] **Update SQL in b2b_demand_gen.py** — Swap TODO placeholders with real table/column names
- [ ] **Test the connection** — `python scheduler.py --once`
- [ ] **Verify dashboard renders with live data** — Check source badge shows "🟢 Live"

### P3: Wire v3.0 to the Backend API

- [ ] **Add fetch() + fallback pattern to v3.0** — Currently all data is hardcoded JS constants. Need to add:
  - `loadDashboardData(startDate, endDate)` async function
  - Fetch from `API_BASE + '/api/b2b-demand-gen'`
  - On success: re-render all sections with live data
  - On failure: keep using hardcoded fallback (current behavior)
  - Wire refresh button to trigger manual fetch
- [ ] **Make date range filter functional** — Date picker dropdown already has CSS, needs:
  - Dropdown open/close on filter pill click
  - Start/end date inputs
  - Apply button triggers `loadDashboardData(start, end)`
- [ ] **Add auto-refresh** — `setInterval` at 86400000ms (24hr)
- [ ] **Add source badge logic** — Show "🟢 Live" when API responds, "🟡 Fallback" when using hardcoded data
- [ ] **Add last-refreshed timestamp** — CSS class `.last-refreshed` already exists

### P4: Dashboard Polish

- [x] **KPI Sparklines** — ✅ Added 14-month trend sparklines to 5 of 6 KPI cards (Open Opps skipped — no monthly data)
  - `drawSparkline()` with retina support, hex→rgba gradient fill, theme-aware colors, end dot
  - Wired into theme toggle + resize callbacks
  - Data: Leads (↓), MQLs (↑), MQL Rate (↑), Merchants (↓), Conv Rate (↓)
- [x] **vs. Target section** — ✅ 6 progress bar cards with color-coded pace indicators (✅/⚠️/🔴). Placeholder targets — one-line swap when real numbers available.
- [x] **Donut charts** — ✅ Lead Distribution + MQL Distribution canvas donuts with center totals, legends, theme-aware, retina.
- [ ] **Region filter interactivity** — Make filter pills actually filter data
  - Would need backend to support query params: `/api/b2b-demand-gen?region=US&channel=all`

### P5: Email Alerts

- [ ] **Configure SMTP** — Add credentials to `.env` (SMTP_HOST, SMTP_USER, SMTP_PASSWORD, EMAIL_RECIPIENTS)
- [ ] **Test email digest** — Run scheduler once, verify HTML email arrives
- [ ] **Customize recipients** — Set up distribution list for the team

### P6: External Sharing

- [ ] **Ask IT/security about external sharing** — Can agency vendors access Blockcell?

### P7: Future / Nice-to-Have

- [ ] **Cohort analysis** — Time-to-convert tracking by channel
- [ ] **First-touch vs last-touch attribution** — Compare attribution models
- [ ] **Regional heatmaps** — Geographic performance visualization
- [ ] **Export to PDF** — One-click report generation for stakeholders
- [ ] **Mobile optimization** — Better responsive layout for phone viewing

---

## 📊 Key Data Reference

### KPIs (Feb 2026 vs Feb 2025)
| Metric | TY | LY | Change |
|---|---|---|---|
| Total Leads | 10,232 | 12,789 | -20% |
| Total MQLs | 1,635 | 676 | +142% |
| MQL Rate | 16.0% | 5.3% | +10.7pp |
| Open Opps | 2,793 | 2,847 | -2% |
| Merchants Won | 529 | 1,671 | -68% |
| Conv Rate | 5.2% | 13.1% | -7.9pp |

### Channel Summary (All-Time)
| Channel | Leads | MQLs | MQL Rate | Merchants |
|---|---|---|---|---|
| SEM | 32,881 | 6,242 | 19.0% | 2,458 |
| Paid Social | 6,558 | 1,923 | 29.3% | 29 |
| Programmatic | 1,085 | ~730 | ~67% | 1 |
| ABM | 54 | ~48 | ~89% | 0 |
| Non-Paid | 157,989 | 3,509 | 2.2% | 17,636 |
| **Total** | **198,567** | **12,452** | **6.3%** | **20,124** |

### Snowflake Tables
| Table | Status | What It Has |
|---|---|---|
| `FIVETRAN.MARKETO.LEAD` | ✅ Confirmed access | 11.3M rows, UTM channels, funnel stages, lead sources |
| `AP_MER_ANALYTICS.BETA.SMB_LEADS` | ❌ Need access | Richer: segments, addressability, paid_flag, MQL flag, regional |
| `AP_MER_ANALYTICS.BETA.SALESFORCESQ_OPPORTUNITIES` | ❌ Need access | Opportunity data for conversion tracking |

### Monthly Trend Data (14 months)
```
Month     Leads   MQLs  Merchants  PS    PSoc  Disp   NP
Jan'25    21186    819    1522    2045    47     7   19087
Feb'25    12789    676    1671    1833   127    13   10816
Mar'25    13731    702    1754    2061   179   123   11368
Apr'25    21866    503    1758    1971   200    34   19661
May'25    14308    557    1898    1897   281    23   12107
Jun'25    12871    528    1680    1986   307    39   10539
Jul'25    13194    643    1794    2400   434    52   10308
Aug'25    12756    808    1707    2045   386   122   10203
Sep'25    12586   1138    1395    2784   729    82    8991
Oct'25    12130   1113    1264    2724   615    89    8702
Nov'25    13576    913    1100    2615   675    55   10231
Dec'25    12440    964    1233    2748   321    74    9297
Jan'26    11979   1116     687    2778  1008   140    8053
Feb'26    10232   1635     529    2437   953   240    6602
```

### Lead Sources (All-Time)
| Source | Leads | Merchants | Conv Rate | Badge |
|---|---|---|---|---|
| Self-Serve | 95,326 | 13,093 | 13.7% | Volume Engine 🏭 |
| Contact Us | 42,712 | 2,575 | 6.0% | Quality Problem ⚠️ |
| Historical | 10,394 | 0 | 0% | Legacy Data 📁 |
| Prospecting Tool | 9,702 | 181 | 1.9% | Outbound 📞 |
| Brand Expansion | 1,832 | 702 | 38.3% | Hidden Gem 💎 |
| Content | 1,230 | 4 | 0.3% | Top of Funnel 📝 |
| Partner | 685 | 12 | 1.8% | Partner Referral 🤝 |
| Physical Event | 626 | 2 | 0.3% | Events 🎪 |
| 1:1 Merchant Intro | 288 | 115 | 39.9% | Quality King 👑 |

### Funnel Stages
| Stage | Count | % |
|---|---|---|
| Prospect | 35,158 | 17.7% |
| MQL | 12,449 | 6.3% |
| SQL | 11,776 | 5.9% |
| Open Opportunity | 44,044 | 22.2% |
| Merchant (Won) | 18,235 | 9.2% |
| Disqualified | 26,767 | 13.5% |
| Closed Lost | 44,841 | 22.6% |
| Nurture | 1,731 | 0.9% |

### Post-Conversion Journey
Get Transacting (256) → Adopt (107) → Boost (587) → Retain (939)

---

## 🔧 Technical Reference

### File Paths
```
/Users/npetrillo/repos/block/
├── b2b-dg-dashboard/
│   ├── afterpay-b2b-demand-gen-v3.html   ← v3.0 dashboard (THE MAIN FILE)
│   └── TODO.md                           ← THIS FILE (single source of truth)
├── monks-lite/
│   ├── afterpay-monks-lite.html          ← Monks v2.0
│   └── TODO.md                           ← Monks task list
├── backend/                              ← Shared backend (serves both dashboards)
│   ├── config.py
│   ├── snowflake_connector.py
│   ├── server.py
│   ├── scheduler.py
│   ├── requirements.txt
│   ├── env.example
│   ├── engines/
│   │   ├── b2b_demand_gen.py
│   │   ├── monks_biweekly.py
│   │   └── insight_engine.py
│   └── notifications/
│       ├── slack_notifier.py
│       └── email_notifier.py
└── README.md
```

### v3.0 Dashboard Architecture
- **CSS:** ~340 lines, dark/light theme vars, 30+ component classes
- **HTML:** ~1,300 lines across 5 tab panels
- **JS:** ~400 lines in single IIFE with 14 functions:
  1. Main tab switching (pill buttons)
  2. Theme toggle (localStorage + auto-detect + themeChangeCallbacks array)
  3. IntersectionObserver for .animate-in
  4. drawLeadChart() — horizontal grouped bars (Overview)
  5. Channel Deep Dive inner tab switching (dd-tab, scoped to .tabs-container)
  6. drawConvRateChart() — horizontal sorted bars (Lead Sources)
  7. drawTrendsLeadChart() — vertical bars + MQL line overlay (Trends)
  8. drawTrendsMerchantChart() — green-to-red gradient bars (Trends)
  9. drawChannelMixChart() — stacked vertical bars (Trends)
  10. renderTargetCards() — vs. Target progress bars with pace indicators
  11. drawDonut() / drawAllDonuts() — Lead + MQL distribution donuts
  12. drawSparkline() / drawAllSparklines() — KPI trend sparklines
  13. hexToRgba() — color utility for gradient fills
- **All charts:** retina (devicePixelRatio), theme-aware (getComputedStyle), resize-debounced

### Backend API Endpoints
| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check |
| `/api/b2b-demand-gen` | GET | Full dashboard payload |
| `/api/monks-biweekly` | GET | Monks dashboard payload |
| `/api/b2b-demand-gen/alerts` | GET | Alerts only |
| `/api/monks-biweekly/alerts` | GET | Monks alerts only |
| `/api/refresh` | POST | Trigger manual refresh |

### Design System
- Font: Inter (Google Fonts)
- Dark: bg #0f0f1a, card #1c1c30, text #e8e8f0, accent #4ecdc4
- Light: bg #f0f2f5, card #ffffff, text #1a1a2e, accent #2fb8ad
- Colors: green #34d399, red #f87171, amber #fbbf24, purple #a78bfa, blue #60a5fa, pink #f472b6
- Responsive breakpoints: 1100px, 700px

---

## 📝 Session Notes for Goose

**IMPORTANT:** When starting a new session, say:
> *"Read /Users/npetrillo/repos/block/b2b-dg-dashboard/TODO.md — it has all the context. Don't search chat history or use chatrecall. Pick up from the TODO list."*

**Rules for working on this project:**
1. **Never search chat history** — it bloats context and causes tool failures
2. **Read `b2b-dg-dashboard/TODO.md`** at the start of each session — it has everything
3. **Update `b2b-dg-dashboard/TODO.md`** at the end of each session — check off completed items, add new ones
4. **One section at a time** — don't try to rewrite the whole HTML file at once
5. **Use str_replace** for targeted edits — don't rewrite entire files
6. **Keep the v3.0 HTML file at its current path** — `/Users/npetrillo/repos/block/b2b-dg-dashboard/afterpay-b2b-demand-gen-v3.html`

---

*Last updated: March 7, 2026 — v3.0 deployed to Blockcell with sparklines, vs. Target cards, donut charts, source badge. 2,129 lines, 14 JS functions.*
