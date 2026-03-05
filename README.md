# Afterpay Marketing Dashboards 📊

Two self-contained HTML dashboards built for the Afterpay SMB marketing team. No frameworks, no dependencies, no build steps — just open in any browser and go.

---

## 📁 Files

### `afterpay-b2b-demand-gen.html`

**Afterpay B2B Demand Gen Dashboard**

A YoY performance dashboard tracking B2B demand generation across merchant segments (Small, Medium, Premium, Mid-Market).

**What's inside:**
- **KPI Summary** — 6 top-level cards (Total Leads, MQLs, Addressable Leads, Addressability Rate, 28D Close Won Rate, Total Addressable aGPV) with YoY comparisons
- **Big Wins & Watchouts** — At-a-glance insights highlighting what's working and what needs attention
- **Lead Volume by Segment** — Horizontal bar chart (Canvas 2D) comparing TY vs LY across all segments, plus a detailed breakdown table
- **Funnel Visualization** — Side-by-side TY vs LY funnel showing Leads → MQLs → Addressable Leads → 28D Close Won Rate
- **Segment Deep Dive** — Tabbed interface with per-segment metrics, mini bar charts, and YoY change indicators
- **Segment Mix Donuts** — Two donut charts showing Lead Distribution vs Addressable aGPV Distribution (reveals that Mid-Market is 1% of leads but 71% of value)

**Data period:** Jan 1–5, 2026 vs Jan 1–5, 2025

---

### `afterpay-monks-lite.html`

**Afterpay × Monks Biweekly Lite Dashboard** 🍺

A cross-channel performance dashboard designed for biweekly reviews with Monks (agency partner). Covers Paid Social, Programmatic, and Search across US, UK, and ANZ regions.

**What's inside:**
- **Executive Summary** — High-level narrative of the period's performance
- **Channel Temp-Check** — 3 channel cards (Paid Social, Programmatic, Search) with key metrics (Spend, Impressions, Clicks, CTR, Leads, CPL) and status badges (Strong / Mixed / Watch-out)
- **Regional Breakdown** — Tabbed tables for 🇺🇸 US, 🇬🇧 UK, and 🇦🇺 ANZ with per-channel data, YoY changes, and contextual insights
- **Watch-Outs & Action Items** — Prioritized alert cards (Critical / Monitor / Opportunity) with specific recommended actions
- **Share Modal** — Quick-share link for Blockcell-hosted version
- **Staleness Tracker** — 🔔 Bell icon tracks data freshness with a configurable threshold; includes a drag-and-drop file upload zone for updating data

**Data period:** February 1–15, 2026

---

## ✨ Features (Both Dashboards)

| Feature | Details |
|---|---|
| **💡 Light/Dark Mode** | Lightbulb toggle in the top-right corner. Auto-defaults to **light mode** between 9 AM–5 PM and **dark mode** all other hours. Click to manually override anytime. |
| **Zero Dependencies** | Fully self-contained single-file HTMLs. No npm, no build tools, no external JS libraries. Just HTML + CSS + vanilla JS. |
| **Portable** | Open locally in any browser, email to colleagues, host on Blockcell, push to GitHub — works everywhere. |
| **Responsive** | Adapts to different screen sizes with CSS grid breakpoints. |
| **Smooth Animations** | Scroll-triggered fade-ins, hover effects, and 0.3s theme transitions. |

---

## 🚀 How to Use

1. **Open locally** — Double-click either `.html` file to open in your default browser
2. **Share with others** — Send the file directly via Slack, email, or Google Drive. Recipients just open it in their browser.
3. **Host internally** — Push to Blockcell for a persistent internal URL
4. **Toggle theme** — Click the 💡 lightbulb in the top-right to switch between light and dark mode

---

## 🛠 Built With

- **HTML5 / CSS3 / Vanilla JavaScript**
- **Canvas 2D API** for charts (no Chart.js or D3 needed)
- **Google Fonts** — Inter (the only external dependency; degrades gracefully to system fonts)
- **Goose** 🪿 — AI-assisted development

---

## 📝 Notes

- All data is **static/hardcoded** — these are prototype dashboards for presentation and review purposes
- The B2B Demand Gen dashboard is tagged as `Prototype — Static Data`
- The Monks Biweekly dashboard includes a file upload zone (staleness tracker) designed to work with Goose for future data refresh workflows
- Date ranges are small sample sizes — interpret trends with caution

---

*Made with ❤️ by Nick and Goose 🪿*
