# Afterpay B2B Growth Marketing Dashboards 📊

Two interactive HTML dashboards for the Afterpay B2B Growth Marketing team, powered by a Python backend connected to Snowflake. The B2B Demand Gen dashboard now runs on **real production data** from `FIVETRAN.MARKETO.LEAD` — 11.3M rows of Afterpay lead data with full funnel tracking.

> **What changed in v2.1?** The B2B dashboard is now powered by **real Snowflake data** (15 months, Jan 2025 – Mar 2026). It shifted from segment-based analytics (Small/Medium/Premium) to **channel-based analytics** (Paid Search, Paid Social, Paid Display, Non-Paid) with full funnel tracking from Lead → MQL → SQL → Opportunity → Merchant.

---

## 📁 Project Structure

```
block/
├── afterpay-b2b-demand-gen.html    ← B2B Demand Gen Dashboard (v2.1 — LIVE DATA)
├── afterpay-monks-lite.html        ← Monks Biweekly Dashboard (v2.0)
├── README.md                       ← You are here
└── backend/                        ← Python backend (API + scheduler + notifications)
    ├── config.py                   ← Environment variables & alert thresholds
    ├── snowflake_connector.py      ← Snowflake client with context manager
    ├── server.py                   ← FastAPI server (JSON endpoints)
    ├── scheduler.py                ← Daily refresh job + uvicorn launcher
    ├── requirements.txt            ← pip dependencies
    ├── env.example                 ← Template for .env configuration
    ├── engines/
    │   ├── b2b_demand_gen.py       ← B2B data engine (Snowflake queries + YoY calcs)
    │   ├── monks_biweekly.py       ← Monks data engine (channel × region queries)
    │   └── insight_engine.py       ← Shared formatting & narrative generation
    └── notifications/
        ├── slack_notifier.py       ← Slack webhook alerts & summaries
        └── email_notifier.py       ← SMTP email digests & staleness warnings
```

---

## 📊 Dashboard 1: B2B Demand Gen

**`afterpay-b2b-demand-gen.html`** — YoY performance tracking by marketing channel

> 🟢 **Now powered by real Snowflake data** from `FIVETRAN.MARKETO.LEAD` (11.3M rows)

### What's Inside
- **KPI Summary** — 6 cards: Total Leads, MQLs, MQL Rate, Open Opps, Merchants Won, Conversion Rate
- **Dynamic Wins & Watchouts** — Auto-generated insights from real data (MQL surge, conversion bottlenecks, channel efficiency)
- **Lead Volume by Channel** — Horizontal bar chart (Canvas 2D) comparing Feb 2026 vs Feb 2025
- **Detailed Breakdown Table** — Channel-level metrics: Leads, MQLs, Opps, Won with YoY changes
- **Funnel Visualization** — Side-by-side YoY funnel (Leads → MQLs → Opportunities → Merchants Won)
- **Channel Deep Dive** — Tabbed interface: Paid Search, Paid Social, Paid Display, Non-Paid, All Channels
- **Channel Mix Donuts** — Lead Distribution vs MQL Distribution by channel

### v2.1 Features (NEW — Real Data!)
| Feature | Details |
|---|---|
| 🔥 **Real Snowflake Data** | 15 months of live Afterpay lead data (Jan 2025 – Mar 2026) from `FIVETRAN.MARKETO.LEAD` |
| 📊 **Channel-Based Analytics** | Shifted from segments (Small/Medium/Premium) to channels (Paid Search, Paid Social, Paid Display, Non-Paid) |
| 🔻 **Full Funnel Tracking** | Leads → MQL → SQL → Open Opportunity → Merchant Won |
| 🎯 **Real Insights** | MQLs +142% YoY, Paid Social +650%, MQL rate 5.3% → 16.0%, conversion bottleneck detected |
| 🔄 **Refresh Button** | Pull latest data from the API with spinning animation |
| 🟢/🟡 **Source Badge** | "Live" (green) when connected to Snowflake, "Fallback" (amber) when offline |
| 📈 **KPI Sparklines** | Trend indicators on each KPI card |
| 📅 **Date Range Picker** | Custom start/end date selection |
| ⏰ **Auto-Refresh** | 24-hour refresh cycle |
| 🛡️ **Graceful Fallback** | Real data baked in — dashboard works standalone without the backend |

### Data Source
| Field | Value |
|---|---|
| **Table** | `FIVETRAN.MARKETO.LEAD` |
| **Filter** | `AFTERPAY_BU = 'Afterpay'` |
| **Date Column** | `CREATED_AT` |
| **Channel Logic** | `LAST_TOUCH_UTM_MEDIUM_C`: cpc → Paid Search, p-social → Paid Social, disp → Paid Display, else → Non-Paid |
| **Funnel Column** | `PROSPECT_LIFECYCLE_STATUS_C`: MQL, SQL, Open Opportunity, Merchant, Disqualified, Closed Lost |

**Default data period:** Feb 2026 vs Feb 2025

---

## 📡 Dashboard 2: Monks Biweekly Lite

**`afterpay-monks-lite.html`** — Cross-channel performance for biweekly agency reviews

### What's Inside
- **Executive Summary** — Auto-generated narrative paragraph from the data
- **Channel Temp-Check** — 3 channel cards (Paid Social, Programmatic, Search) with status badges
- **💰 Spend Allocation Donut** *(NEW in v2.0)* — Visual breakdown of where budget is going
- **Regional Breakdown** — Tabbed tables for 🇺🇸 US, 🇬🇧 UK, and 🇦🇺 ANZ
- **🗺️ Regional Performance Heatmap** *(NEW in v2.0)* — 3×3 grid color-coded by Win/Mixed/Watch-out
- **Watch-Outs & Action Items** — Auto-prioritized alert cards (Critical → Monitor → Opportunity)
- **Share Modal** — Quick-share link for Blockcell-hosted version
- **Staleness Tracker** — 🔔 Bell icon now auto-detects freshness from API data

### v2.0 Features
| Feature | Details |
|---|---|
| 🔄 **Refresh Button** | Manual data refresh with spinning animation. |
| 🟢/🟡 **Source Badge** | Live vs Fallback indicator. |
| 🕐 **Last Refreshed** | Auto-updating timestamp. |
| 🍩 **Spend Donut** | NEW — Canvas 2D donut showing spend allocation across channels. |
| 🗺️ **Heatmap** | NEW — 3×3 region × channel grid with color-coded performance status. |
| 📝 **Dynamic Rendering** | Exec summary, channel cards, regional tables, and alert cards all render from API data. |
| 🔔 **Smart Staleness** | Staleness tracker now reads from API timestamp instead of hardcoded date. |
| ⏰ **Auto-Refresh** | 24-hour refresh cycle. |

**Default data period:** February 1–15, 2026

---

## 🐍 Python Backend

The backend is the brain that makes everything live. It connects to Snowflake, computes metrics, generates insights, serves data via API, and sends notifications.

### Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Snowflake   │────▶│  Python Backend   │────▶│ Notifications │
│  (tables)    │     │  (FastAPI + APSch)│     │ (Slack/Email) │
└─────────────┘     └────────┬─────────┘     └──────────────┘
                             │
                    ┌────────▼─────────┐
                    │  HTML Dashboards  │
                    │  (fetch JSON API) │
                    └──────────────────┘
```

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check + cache status |
| `/api/b2b-demand-gen` | GET | Full B2B dashboard payload (KPIs, segments, insights) |
| `/api/monks-biweekly` | GET | Full Monks dashboard payload (channels, regions, alerts) |
| `/api/b2b-demand-gen/alerts` | GET | B2B insights only |
| `/api/monks-biweekly/alerts` | GET | Monks alerts only |
| `/api/refresh` | POST | Trigger manual refresh of both dashboards |

### Alert Engine

The backend auto-generates alerts based on configurable thresholds:

| Alert | Trigger | Severity |
|---|---|---|
| Lead volume collapse | Any region×channel leads drop > 40% | 🔴 Critical |
| CPL explosion | CPL exceeds $1,000 | 🔴 Critical |
| Close-won rate drop | Rate drops > 30% WoW | 🔴 Critical |
| Form drop-off | Form start → lead conversion > 70% drop | 🔴 Critical |
| CPL doubling | CPL increases > 80% vs prior | 🟡 Monitor |
| Global CPL drift | Overall CPL trending up | 🟡 Monitor |
| Efficient CPL | CPL < $50 with 100+ leads | 🟢 Opportunity |
| Lead surge | Leads up > 50% with stable CPL | 🟢 Opportunity |

### Notifications

- **Slack** — Rich Block Kit messages for critical/monitor alerts + daily summaries
- **Email** — HTML digest tables for critical alerts + staleness warnings
- **Staleness** — Auto-warns when data hasn't refreshed beyond the threshold (default: 14 days)

---

## 🚀 Getting Started

### Quick Start (Dashboards Only)

Just open either `.html` file in your browser. They work standalone with fallback data — no backend required.

### Full Setup (Live Data)

```bash
# 1. Clone the repo
git clone https://github.com/npetrillo-block/block.git
cd block/backend

# 2. Configure environment
cp env.example .env
# Edit .env with your Snowflake credentials, Slack webhook, SMTP settings

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the backend
python scheduler.py              # Starts API server + daily scheduler at 7 AM
# OR
python scheduler.py --once       # One-time refresh (good for testing)

# 5. Update API_BASE in both HTML files
# Change 'http://localhost:8000' to your server URL if deploying remotely
```

### Configuration (env.example)

| Variable | Description |
|---|---|
| `SNOWFLAKE_ACCOUNT` | Your Snowflake account identifier |
| `SNOWFLAKE_USER` / `PASSWORD` | Snowflake credentials |
| `SNOWFLAKE_WAREHOUSE` / `DATABASE` / `SCHEMA` | Snowflake connection details |
| `B2B_LEADS_TABLE` | Table for B2B lead data |
| `MONKS_CHANNEL_TABLE` | Table for channel performance data |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook for notifications |
| `SMTP_HOST` / `SMTP_USER` / `SMTP_PASSWORD` | Email SMTP settings |
| `EMAIL_RECIPIENTS` | Comma-separated alert recipients |
| `REFRESH_HOUR` / `REFRESH_MINUTE` | Daily refresh time (default: 7:00 AM) |
| `STALENESS_THRESHOLD_DAYS` | Days before data is flagged stale (default: 14) |

---

## ✨ Shared Features (Both Dashboards)

| Feature | Details |
|---|---|
| **💡 Light/Dark Mode** | Lightbulb toggle. Auto-defaults to light (9 AM–5 PM) and dark (all other hours). |
| **Zero Dependencies** | Self-contained HTML files. No npm, no build tools. |
| **Portable** | Open locally, email, host on Blockcell, push to GitHub. |
| **Responsive** | CSS grid breakpoints for different screen sizes. |
| **Smooth Animations** | Scroll-triggered fade-ins, hover effects, 0.3s theme transitions. |
| **Graceful Degradation** | Dashboards always render — with live data when available, fallback data when not. |

---

## 🛠 Built With

- **HTML5 / CSS3 / Vanilla JavaScript** — Zero-dependency frontend
- **Canvas 2D API** — Charts, donuts, sparklines (no Chart.js or D3)
- **Python 3.10+** — Backend runtime
- **FastAPI** — REST API server
- **APScheduler** — Daily refresh scheduling
- **snowflake-connector-python** — Snowflake data access
- **Google Fonts** — Inter (degrades gracefully to system fonts)
- **Goose** 🪿 — AI-assisted development

---

## 📝 Status & Notes

- **B2B Dashboard** — ✅ Live! Powered by real data from `FIVETRAN.MARKETO.LEAD`. Works standalone (real data baked into fallback) or with the Python backend for auto-refresh.
- **Monks Dashboard** — Still uses fallback data. Needs manual .xlsx handoff from agency partner.
- **Backend** — Snowflake credentials still need to be configured in `.env` for automated daily refresh. The confirmed working table is `FIVETRAN.MARKETO.LEAD`.
- **Slack/Email Notifications** — Code is built and ready. Just needs Slack webhook URL and SMTP credentials in `.env`.
- **Next up (v3.0)** — Full dashboard redesign: live funnel visualization, cohort analysis, first-touch vs last-touch attribution, time-to-convert tracking, regional heatmaps.
- Alert thresholds are configurable in `backend/config.py`.

---

## 📋 Version History

| Version | Date | What Changed |
|---|---|---|
| **v2.1** | Mar 6, 2026 | 🔥 **Real Snowflake data!** B2B dashboard powered by `FIVETRAN.MARKETO.LEAD` (11.3M rows). Channel-based analytics (Paid Search/Social/Display/Non-Paid). Full funnel tracking (Lead → MQL → SQL → Opp → Merchant). 15 months of live data. Real auto-generated insights. |
| v2.0 | Mar 5, 2026 | 🚀 Live data layer — Python backend, Snowflake integration, API endpoints, auto-refresh, dynamic rendering, sparklines, spend donut, regional heatmap, Slack/email alerts, staleness auto-detection |
| v1.3–1.4 | Mar 4, 2026 | Light/dark mode toggle, staleness tracker, share modal, file upload zone |
| v0.2 | Feb 26, 2026 | Initial B2B dashboard with Canvas 2D charts |
| v0.1 | Feb 25, 2026 | First Monks Biweekly prototype |

---

*Made with ❤️ by Nick and Goose 🪿*
