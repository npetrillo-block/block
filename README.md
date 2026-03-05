# Afterpay Marketing Dashboards 📊

**v2.0 — Live Dashboards with Python Backend**

Two interactive HTML dashboards for the Afterpay SMB marketing team, now powered by a Python backend that connects to Snowflake, auto-refreshes daily, and sends Slack/email alerts when red flags pop up.

> **What changed in v2.0?** These dashboards evolved from static, read-only HTML prototypes into live tools that pull data from Snowflake, refresh their visualizations automatically, generate commentary on the fly, and notify you when something needs attention.

---

## 📁 Project Structure

```
block/
├── afterpay-b2b-demand-gen.html    ← B2B Demand Gen Dashboard (v2.0)
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

**`afterpay-b2b-demand-gen.html`** — YoY performance tracking across merchant segments

### What's Inside
- **KPI Summary** — 6 top-level cards with YoY comparisons + sparkline trend indicators
- **Dynamic Wins & Watchouts** — Auto-generated insights based on data thresholds (not hardcoded)
- **Lead Volume by Segment** — Horizontal bar chart (Canvas 2D) comparing TY vs LY
- **Detailed Breakdown Table** — Segment-level metrics with color-coded YoY changes
- **Funnel Visualization** — Side-by-side TY vs LY funnel (Leads → MQLs → Addressable → Close Won)
- **Segment Deep Dive** — Tabbed interface with per-segment metrics and mini bar charts
- **Segment Mix Donuts** — Lead Distribution vs Addressable aGPV Distribution

### v2.0 Features
| Feature | Details |
|---|---|
| 🔄 **Refresh Button** | Click to pull latest data from the API. Spinning animation while loading. |
| 🟢/🟡 **Source Badge** | Shows "Live" (green) when connected to Snowflake, "Fallback" (amber) when using static data. |
| 🕐 **Last Refreshed** | Timestamp showing when data was last pulled. |
| 📈 **KPI Sparklines** | Tiny trend charts on each KPI card showing directional momentum. |
| 📅 **Date Range Picker** | Click the Date Range filter to select custom start/end dates. |
| ⏰ **Auto-Refresh** | Refreshes every 24 hours automatically. |
| 🛡️ **Graceful Fallback** | If the API is down, dashboard renders with the last known static data — never breaks. |

**Default data period:** Jan 1–5, 2026 vs Jan 1–5, 2025

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

- **WIP** — Snowflake table names and credentials are placeholders (`TODO_*`). Fill in your `.env` to go live.
- The backend gracefully falls back to static data when Snowflake is unavailable — dashboards never break.
- Alert thresholds are configurable in `backend/config.py`.
- Date ranges in the fallback data are small sample sizes — interpret trends with caution.

---

## 📋 Version History

| Version | Date | What Changed |
|---|---|---|
| **v2.0** | Mar 2026 | 🚀 Live data layer — Python backend, Snowflake integration, API endpoints, auto-refresh, dynamic rendering, sparklines, spend donut, regional heatmap, Slack/email alerts, staleness auto-detection |
| v1.3–1.4 | Mar 2026 | Light/dark mode toggle, staleness tracker, share modal, file upload zone |
| v0.2 | Mar 2026 | Initial B2B dashboard with Canvas 2D charts |
| v0.1 | Mar 2026 | First Monks Biweekly prototype |

---

*Made with ❤️ by Nick and Goose 🪿*
