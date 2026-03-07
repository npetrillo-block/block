# Afterpay B2B Growth Marketing Dashboards 📊

**v3.0 — Multi-Tab Analytics Dashboard Powered by Real Snowflake Data**

Interactive HTML dashboards for the Afterpay B2B Growth Marketing team, backed by a Python backend connected to Snowflake. The B2B Demand Gen dashboard runs on **real production data** from `FIVETRAN.MARKETO.LEAD` — 11.3M rows of Afterpay lead data with full funnel tracking across 5 dedicated tabs.

> **What's new in v3.0?** Complete dashboard rebuild with 5 dedicated tabs (Overview, Channels, Lead Sources, Funnel, Trends), 5 retina Canvas 2D charts, channel deep-dive with inner tabs, 9 lead source cards, vertical funnel visualization, post-conversion journey flow, and 14-month trend analysis. All theme-aware with dark/light mode.

---

## 📁 Project Structure

```
block/
├── afterpay-b2b-demand-gen-v3.html ← B2B Demand Gen Dashboard (v3.0 — LATEST)
├── afterpay-b2b-demand-gen.html    ← B2B Demand Gen Dashboard (v2.1 — legacy)
├── afterpay-monks-lite.html        ← Monks Biweekly Dashboard (v2.0)
├── README.md                       ← You are here
├── TODO.md                         ← Master task list & project context
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

## 📊 Dashboard 1: B2B Demand Gen (v3.0)

**`afterpay-b2b-demand-gen-v3.html`** — 1,905-line multi-tab analytics dashboard

> 🟢 **Powered by real Snowflake data** from `FIVETRAN.MARKETO.LEAD` (11.3M rows, 15 months: Jan 2025 – Feb 2026)

### 5 Tabs

| Tab | What's Inside |
|---|---|
| **📊 Overview** | 6 KPI cards, Wins & Watchouts (6+6), Lead Volume bar chart + breakdown table, Channel Deep Dive (5 inner tabs × 4-6 metric cards), All-Time Performance table, SEM Regional table, vs. Target placeholder |
| **📡 Channels** | 5 channel group cards with colored top borders — SEM, Paid Social (Meta vs LinkedIn), Programmatic (DV360), ABM (6sense + Demandbase), Non-Paid |
| **🔗 Lead Sources** | 9 source cards with colored badges + mini funnels, Conversion Rate by Source horizontal bar chart |
| **🔻 Funnel** | Vertical pipeline (Prospect → MQL → SQL → Open Opp → Merchant Won), Exit Paths, Post-Conversion Journey |
| **📈 Trends** | Monthly Leads & MQLs (bars + line), Monthly Merchants Won (gradient), Channel Mix Over Time (stacked), 3 insight callouts |

### Design Features
| Feature | Details |
|---|---|
| 🌙💡 **Dark/Light Mode** | Lightbulb toggle, auto-detects (light 9am-5pm), persists to localStorage |
| 🟢 **Live Badge** | Pulsing green dot with "Live" indicator |
| 🎨 **Gradient Title** | CSS gradient text (accent → purple) |
| 📱 **Responsive** | CSS grid breakpoints at 1100px and 700px |
| 📊 **5 Retina Charts** | All canvas charts use devicePixelRatio, theme-aware colors |

### Data Source
| Field | Value |
|---|---|
| **Table** | `FIVETRAN.MARKETO.LEAD` |
| **Filter** | `AFTERPAY_BU = 'Afterpay'` |
| **Channel Logic** | `LAST_TOUCH_UTM_MEDIUM_C`: cpc → Paid Search, p-social → Paid Social, disp → Display, else → Non-Paid |
| **Funnel Column** | `PROSPECT_LIFECYCLE_STATUS_C` |
| **Lead Source** | `LEAD_SOURCE_CHANNEL_C` |

---

## 📡 Dashboard 2: Monks Biweekly Lite (v2.0)

**`afterpay-monks-lite.html`** — Cross-channel performance for biweekly agency reviews

- Executive Summary, Channel Temp-Check, Spend Allocation Donut, Regional Breakdown, Heatmap, Watch-Outs & Action Items

---

## 🐍 Python Backend

```
Snowflake → Python Backend (FastAPI + APScheduler) → JSON API → HTML Dashboards
                                                   → Slack/Email Notifications
```

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check |
| `/api/b2b-demand-gen` | GET | Full B2B dashboard payload |
| `/api/monks-biweekly` | GET | Monks dashboard payload |
| `/api/refresh` | POST | Trigger manual refresh |

**Notifications:** Slack (Block Kit alerts) + Email (HTML digests) — code built, needs webhook URL and SMTP creds.

---

## 🚀 Getting Started

### Quick Start (Dashboards Only)
Open `afterpay-b2b-demand-gen-v3.html` in your browser. Works standalone — no backend required.

### Full Setup (Live Data)
```bash
git clone https://github.com/npetrillo-block/block.git
cd block/backend
cp env.example .env    # Edit with Snowflake creds, Slack webhook, SMTP
pip install -r requirements.txt
python scheduler.py    # Starts API + daily scheduler
```

---

## 📝 Status & Roadmap

See **[TODO.md](TODO.md)** for the full task list.

| Item | Status |
|---|---|
| v3.0 Dashboard | ✅ Complete (1,905 lines, 5 tabs, 5 charts) |
| Python Backend | ✅ Built, needs Snowflake creds |
| Slack Integration | 🔜 Code ready, needs webhook URL |
| Blockcell Deploy | 🔜 v3.0 needs publishing |
| Live Data Connection | 🔜 Needs Snowflake service account |

---

## 📋 Version History

| Version | Date | What Changed |
|---|---|---|
| **v3.0** | Mar 7, 2026 | 🏗️ Complete rebuild — 5 tabs, 5 charts, 1,905 lines |
| v2.1 | Mar 6, 2026 | Real Snowflake data, channel-based analytics |
| v2.0 | Mar 5, 2026 | Python backend, API, Slack/email alerts |
| v1.3–1.4 | Mar 4, 2026 | Light/dark mode, staleness tracker |
| v0.2 | Feb 26, 2026 | Initial dashboard |

---

## 🛠 Built With

HTML5/CSS3/Vanilla JS · Canvas 2D API · Python 3 · FastAPI · APScheduler · snowflake-connector-python · Inter (Google Fonts) · Goose 🪿
