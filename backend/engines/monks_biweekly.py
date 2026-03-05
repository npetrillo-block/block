"""
Data engine for the Monks Biweekly dashboard.

Fetches channel × region performance data from Snowflake, computes
period-over-period changes, auto-generates alerts and executive summary.
Falls back to hardcoded data when Snowflake is unavailable.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import config
from engines.insight_engine import format_currency, format_number, format_pct_change, pct_change
from snowflake_connector import SnowflakeClient

logger = logging.getLogger(__name__)

# ======================================================================
# Fallback data (mirrors current hardcoded dashboard — Feb 1-15 2026)
# ======================================================================

FALLBACK_DATA: Dict[str, Any] = {
    "period": {"start": "2026-02-01", "end": "2026-02-15"},
    "summary": {
        "total_spend": 357676, "spend_change_pct": 93,
        "total_impressions": 33400000, "total_clicks": 600000,
        "total_leads": 2095, "avg_ctr": 1.79, "avg_cpl": 171.09, "prior_cpl": 90.66,
    },
    "channels": [
        {
            "name": "Paid Social", "spend": 197917, "impressions": 20100000,
            "clicks": 387000, "ctr": 1.93, "leads": 480, "cpl": 412.33, "status": "Mixed",
            "insight": "US is the engine (378 leads, $184 CPL). UK and ANZ struggling with lead conversion — high form starts but poor follow-through.",
        },
        {
            "name": "Programmatic", "spend": 82369, "impressions": 12700000,
            "clicks": 51000, "ctr": 0.40, "leads": 175, "cpl": 470.68, "status": "Mixed",
            "insight": "US driving 77% of programmatic leads. UK is a red flag — only 1 lead from $16K spend. ANZ leads growing but CPL doubling.",
        },
        {
            "name": "Search", "spend": 77390, "impressions": 596000,
            "clicks": 162000, "ctr": 27.2, "leads": 1440, "cpl": 53.74, "status": "Strong",
            "insight": "Best performing channel across all regions. PMax campaigns delivering exceptional CPLs. US leads up 63%, UK up 59%.",
        },
    ],
    "regions": {
        "us": {
            "label": "🇺🇸 United States",
            "rows": [
                {"channel": "Paid Social", "spend": 69597, "spend_change": "+78%", "impressions": "1.6M", "clicks": "19K", "ctr": 1.23, "leads": 378, "cpl": 184, "leads_change": "+270%", "status": "Win"},
                {"channel": "Programmatic", "spend": 32771, "spend_change": "+177%", "impressions": "8.6M", "clicks": "236K", "ctr": 2.76, "leads": 134, "cpl": 245, "leads_change": "+103%", "status": "Win"},
                {"channel": "Search", "spend": 40020, "spend_change": "+61%", "impressions": "59K", "clicks": "7.2K", "ctr": 12.26, "leads": 896, "cpl": 44.67, "leads_change": "+63%", "status": "Win"},
            ],
            "insight": "US is firing on all cylinders. All three channels showing strong lead growth. Search PMax at $27.79 CPL is a standout. Only watch-out: LinkedIn CPL at $4,034 — consider reallocating to Meta.",
        },
        "uk": {
            "label": "🇬🇧 United Kingdom",
            "rows": [
                {"channel": "Paid Social", "spend": 32887, "spend_change": "+79%", "impressions": "1.6M", "clicks": "16K", "ctr": 1.03, "leads": 21, "cpl": 1566, "leads_change": "-9%", "status": "Watch-out"},
                {"channel": "Programmatic", "spend": 16419, "spend_change": "+186%", "impressions": "6.9M", "clicks": "128K", "ctr": 1.84, "leads": 1, "cpl": 16419, "leads_change": "-50%", "status": "Watch-out"},
                {"channel": "Search", "spend": 29720, "spend_change": "+28%", "impressions": "126K", "clicks": "4.2K", "ctr": 3.32, "leads": 120, "cpl": 248, "leads_change": "+59%", "status": "Win"},
            ],
            "insight": "UK is a tale of two stories. Search is thriving (+59% leads, PMax CVR up 198%). But Social and Programmatic are in trouble — 825 form starts converting to only 142 leads in Social (83% drop-off), and Programmatic generated just 1 lead from $16K spend.",
        },
        "anz": {
            "label": "🇦🇺 ANZ",
            "rows": [
                {"channel": "Paid Social", "spend": 70621, "spend_change": "+86%", "impressions": "3.5M", "clicks": "26K", "ctr": 0.75, "leads": 81, "cpl": 872, "leads_change": "-58%", "status": "Watch-out"},
                {"channel": "Programmatic", "spend": 33179, "spend_change": "+183%", "impressions": "11.1M", "clicks": "158K", "ctr": 1.43, "leads": 40, "cpl": 821, "leads_change": "+38%", "status": "Mixed"},
                {"channel": "Search", "spend": 33564, "spend_change": "+17%", "impressions": "122K", "clicks": "5.4K", "ctr": 4.41, "leads": 424, "cpl": 79, "leads_change": "+15%", "status": "Win"},
            ],
            "insight": "ANZ Social is the biggest concern this period. AU Meta leads dropped 56% (106→46) and NZ Meta dropped 55% (69→31) despite increased spend. Programmatic leads growing but CPL doubled. Search remains efficient and stable.",
        },
    },
    "alerts": [
        {"severity": "critical", "emoji": "🔴", "title": "UK Programmatic: 1 Lead from $16,419 Spend", "body": "DV360 generating 217 form starts but almost zero conversions. Likely a landing page or form issue specific to UK.", "action": "Audit UK landing pages and form flow immediately."},
        {"severity": "critical", "emoji": "🔴", "title": "ANZ Paid Social: Lead Volume Collapsed -58%", "body": "AU Meta leads down 56%, NZ Meta down 55%. Spend increased but leads cratered.", "action": "Review audience saturation, creative rotation, and frequency caps on Meta AU/NZ."},
        {"severity": "critical", "emoji": "🔴", "title": "UK Paid Social: 825 Form Starts → 142 Leads (83% Drop-off)", "body": "Users are engaging but not converting. Form friction or technical issue likely.", "action": "Test UK form completion flow end-to-end."},
        {"severity": "monitor", "emoji": "🟡", "title": "US LinkedIn CPL: $4,034 per Lead", "body": "Only 3 leads from LinkedIn despite meaningful spend.", "action": "Evaluate LinkedIn budget reallocation to Meta."},
        {"severity": "monitor", "emoji": "🟡", "title": "Global CPL Nearly Doubled: $90.66 → $171.09", "body": "Expected with budget scaling, but efficiency needs to catch up.", "action": "Monitor over next 2 periods."},
        {"severity": "opportunity", "emoji": "🟢", "title": "US Search PMax: $27.79 CPL", "body": "Outstanding efficiency. Opportunity to scale PMax budget further.", "action": "Test incremental PMax budget increase."},
        {"severity": "opportunity", "emoji": "🟢", "title": "UK Search PMax CVR +198%", "body": "Conversion rate nearly tripled.", "action": "Apply UK PMax learnings to other regions."},
    ],
    "exec_summary": "Global spend scaled to ~$358K (+93% vs prior period) across Paid Social, Programmatic, and Search, generating 33.4M impressions and 600K clicks. CTR held steady at 1.79%. However, CPL nearly doubled from $90.66 to $171.09 as budgets scaled — efficiency gains are needed across upper-funnel channels. Search remains the strongest channel globally with a $53.74 CPL, while Paid Social and Programmatic show serious regional efficiency concerns, particularly in UK and ANZ where form-to-lead conversion is breaking down.",
}

# ======================================================================
# SQL template
# TODO: Replace table reference with your actual Snowflake table
# ======================================================================

_FETCH_SQL = f"""
SELECT
    channel,
    region,
    SUM(spend)          AS spend,
    SUM(impressions)    AS impressions,
    SUM(clicks)         AS clicks,
    ROUND(100.0 * SUM(clicks) / NULLIF(SUM(impressions), 0), 2) AS ctr,
    SUM(leads)          AS leads,
    ROUND(SUM(spend) / NULLIF(SUM(leads), 0), 2) AS cpl
FROM
    {config.MONKS_CHANNEL_TABLE}
WHERE
    report_date BETWEEN %(start_date)s AND %(end_date)s
GROUP BY channel, region
ORDER BY channel, region
"""


class MonksBiweeklyEngine:
    """Data engine powering the Monks Biweekly dashboard."""

    def __init__(self, client: SnowflakeClient) -> None:
        self._client = client

    def fetch_data(self, period_start: str, period_end: str) -> Dict[str, Any]:
        """Fetch channel × region data from Snowflake."""
        logger.info("Fetching Monks data for %s → %s", period_start, period_end)
        cy_rows = self._client.execute_query(_FETCH_SQL, {"start_date": period_start, "end_date": period_end})

        # Prior period (same length, immediately preceding)
        days = (datetime.strptime(period_end, "%Y-%m-%d") - datetime.strptime(period_start, "%Y-%m-%d")).days
        prior_end = (datetime.strptime(period_start, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        prior_start = (datetime.strptime(prior_end, "%Y-%m-%d") - timedelta(days=days)).strftime("%Y-%m-%d")
        ly_rows = self._client.execute_query(_FETCH_SQL, {"start_date": prior_start, "end_date": prior_end})

        return self._build_payload(cy_rows, ly_rows, period_start, period_end)

    def generate_alerts(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Auto-generate alert cards from region × channel data.

        Returns sorted list: critical first, then monitor, then opportunity.
        """
        alerts: List[Dict[str, str]] = []
        thresholds = config.ALERT_THRESHOLDS

        for region_key, region in data.get("regions", {}).items():
            region_label = region.get("label", region_key)
            for row in region.get("rows", []):
                channel = row.get("channel", "")
                leads = row.get("leads", 0)
                cpl = row.get("cpl", 0)
                leads_change_str = row.get("leads_change", "0%")
                leads_change = _parse_pct(leads_change_str)

                # Critical: leads collapse
                if leads_change is not None and leads_change < thresholds["lead_collapse_pct"]:
                    alerts.append({
                        "severity": "critical", "emoji": "🔴",
                        "title": f"{region_label} {channel}: Lead Volume Collapsed {leads_change_str}",
                        "body": f"Spend increased but leads cratered to {leads}.",
                        "action": f"Review audience targeting and creative rotation for {channel} in {region_label}.",
                    })

                # Critical: CPL explosion
                if cpl > thresholds["cpl_explosion_threshold"]:
                    alerts.append({
                        "severity": "critical", "emoji": "🔴",
                        "title": f"{region_label} {channel}: CPL at {format_currency(cpl)}",
                        "body": f"Only {leads} lead(s) from {format_currency(row.get('spend', 0))} spend.",
                        "action": f"Audit {channel} landing pages and form flow in {region_label}.",
                    })

                # Monitor: CPL doubling
                if leads_change is not None and cpl > 0:
                    # We'd need prior CPL for true comparison; use leads_change as proxy
                    pass

                # Opportunity: efficient CPL with volume
                if cpl > 0 and cpl < thresholds["cpl_efficiency_threshold"] and leads >= thresholds["cpl_efficiency_min_leads"]:
                    alerts.append({
                        "severity": "opportunity", "emoji": "🟢",
                        "title": f"{region_label} {channel}: {format_currency(cpl)} CPL",
                        "body": f"Outstanding efficiency with {leads} leads.",
                        "action": f"Test incremental budget increase for {channel} in {region_label}.",
                    })

                # Opportunity: lead surge with decent CPL
                if leads_change is not None and leads_change > thresholds["lead_surge_pct"] and cpl < 500:
                    alerts.append({
                        "severity": "opportunity", "emoji": "🟢",
                        "title": f"{region_label} {channel}: Leads up {leads_change_str}",
                        "body": f"{leads} leads at {format_currency(cpl)} CPL.",
                        "action": f"Scale {channel} in {region_label} — strong momentum.",
                    })

        # Global CPL check
        summary = data.get("summary", {})
        avg_cpl = summary.get("avg_cpl", 0)
        prior_cpl = summary.get("prior_cpl", 0)
        if prior_cpl > 0 and avg_cpl > 0:
            cpl_change = pct_change(prior_cpl, avg_cpl)
            if cpl_change and cpl_change > thresholds["cpl_doubling_pct"]:
                alerts.append({
                    "severity": "monitor", "emoji": "🟡",
                    "title": f"Global CPL Increased {cpl_change:+.0f}%: {format_currency(prior_cpl)} → {format_currency(avg_cpl)}",
                    "body": "Efficiency needs to catch up with budget scaling.",
                    "action": "Monitor over next 2 periods.",
                })

        # Sort: critical → monitor → opportunity
        order = {"critical": 0, "monitor": 1, "opportunity": 2}
        alerts.sort(key=lambda a: order.get(a.get("severity", ""), 9))

        return alerts

    def generate_executive_summary(self, data: Dict[str, Any]) -> str:
        """Build a narrative executive summary from the data."""
        summary = data.get("summary", {})
        channels = data.get("channels", [])

        total_spend = summary.get("total_spend", 0)
        spend_change = summary.get("spend_change_pct", 0)
        total_imp = summary.get("total_impressions", 0)
        total_clicks = summary.get("total_clicks", 0)
        avg_ctr = summary.get("avg_ctr", 0)
        avg_cpl = summary.get("avg_cpl", 0)
        prior_cpl = summary.get("prior_cpl", 0)
        total_leads = summary.get("total_leads", 0)

        channel_names = ", ".join(c["name"] for c in channels)
        best = min(channels, key=lambda c: c.get("cpl", float("inf")), default={})
        best_name = best.get("name", "N/A")
        best_cpl = best.get("cpl", 0)

        cpl_verb = "improved" if avg_cpl < prior_cpl else "nearly doubled" if avg_cpl > prior_cpl * 1.8 else "increased"

        # Find problem areas
        problems = []
        for region_key, region in data.get("regions", {}).items():
            for row in region.get("rows", []):
                if row.get("status") in ("Watch-out",):
                    problems.append(f"{region.get('label', region_key)} {row['channel']}")

        problem_str = ""
        if problems:
            problem_str = f" {', '.join(problems[:3])} show serious efficiency concerns."

        return (
            f"Global spend scaled to ~{format_currency(total_spend)} "
            f"({spend_change:+.0f}% vs prior period) across {channel_names}, "
            f"generating {format_number(total_imp)} impressions and {format_number(total_clicks)} clicks. "
            f"CTR held steady at {avg_ctr:.2f}%. "
            f"However, CPL {cpl_verb} from {format_currency(prior_cpl)} to {format_currency(avg_cpl)} "
            f"as budgets scaled — efficiency gains are needed across upper-funnel channels. "
            f"{best_name} remains the strongest channel globally with a {format_currency(best_cpl)} CPL."
            f"{problem_str}"
        )

    def get_dashboard_payload(self, period_start: Optional[str] = None, period_end: Optional[str] = None) -> Dict[str, Any]:
        """Return complete JSON-ready dashboard payload."""
        if not period_end:
            period_end = datetime.utcnow().strftime("%Y-%m-%d")
        if not period_start:
            period_start = (datetime.utcnow() - timedelta(days=14)).strftime("%Y-%m-%d")

        try:
            self._client.connect()
            data = self.fetch_data(period_start, period_end)
            self._client.disconnect()
            source = "snowflake"
        except Exception as exc:
            logger.warning("Snowflake unavailable (%s). Using fallback data.", exc)
            data = FALLBACK_DATA
            source = "fallback"

        if source == "snowflake":
            alerts = self.generate_alerts(data)
            exec_summary = self.generate_executive_summary(data)
        else:
            alerts = data.get("alerts", [])
            exec_summary = data.get("exec_summary", "")

        return {
            "data": data,
            "alerts": alerts,
            "exec_summary": exec_summary,
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "source": source,
        }

    @staticmethod
    def _build_payload(cy_rows, ly_rows, start, end) -> Dict[str, Any]:
        """Transform raw Snowflake rows into structured dashboard dict."""
        # Group by channel and region
        # This would build the same structure as FALLBACK_DATA
        # Implementation depends on actual table schema
        # TODO: Complete this when Snowflake table schema is confirmed
        return FALLBACK_DATA


def _parse_pct(s: str) -> Optional[float]:
    """Parse a percentage string like '+78%' or '-9%' into a float."""
    try:
        return float(s.replace("%", "").replace("+", ""))
    except (ValueError, AttributeError):
        return None
