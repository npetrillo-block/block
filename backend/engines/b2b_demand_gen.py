"""
Data engine for the B2B Demand Gen dashboard.

Fetches lead/MQL/addressability/close-won/aGPV data from Snowflake,
computes YoY changes, and auto-generates insight commentary.
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
# Fallback data (mirrors the current hardcoded dashboard — Jan 1-5 2026)
# ======================================================================

FALLBACK_DATA: Dict[str, Any] = {
    "period": {"start": "2026-01-01", "end": "2026-01-05", "ly_start": "2025-01-01", "ly_end": "2025-01-05"},
    "kpis": [
        {"label": "Total Leads", "value": 514, "ly_value": 193, "yoy_pct": 166, "yoy_label": "+166%", "dir": "up", "unit": ""},
        {"label": "Total MQLs", "value": 514, "ly_value": 193, "yoy_pct": 166, "yoy_label": "+166%", "dir": "up", "unit": ""},
        {"label": "Addressable Leads", "value": 230, "ly_value": 59, "yoy_pct": 290, "yoy_label": "+290%", "dir": "up", "unit": ""},
        {"label": "Addressability Rate", "value": 45, "ly_value": 42, "yoy_pct": None, "yoy_label": "+7pp", "dir": "up", "unit": "%"},
        {"label": "28D Close Won Rate", "value": 5.65, "ly_value": 1.69, "yoy_pct": 233, "yoy_label": "+233%", "dir": "up", "unit": "%"},
        {"label": "Total Addr. aGPV", "value": 198250000, "ly_value": 10290000, "yoy_pct": 1826, "yoy_label": "+1,826%", "dir": "up", "unit": "$"},
    ],
    "segments": {
        "small": {
            "name": "Small", "leads": 355, "leads_ly": 145, "mqls": 355, "mqls_ly": 145,
            "addr_leads": 167, "addr_leads_ly": 42, "addr_rate": 47, "addr_rate_ly": 45,
            "close_won": 5.39, "close_won_ly": 0, "agpv": 9740000, "agpv_ly": 2460000,
            "agpv_per_lead": 0.06, "agpv_per_lead_ly": 0.06,
        },
        "medium": {
            "name": "Medium", "leads": 130, "leads_ly": 42, "mqls": 130, "mqls_ly": 42,
            "addr_leads": 52, "addr_leads_ly": 15, "addr_rate": 40, "addr_rate_ly": 36,
            "close_won": 3.85, "close_won_ly": 6.67, "agpv": 18850000, "agpv_ly": 4830000,
            "agpv_per_lead": 0.36, "agpv_per_lead_ly": 0.32,
        },
        "premium": {
            "name": "Premium", "leads": 24, "leads_ly": 6, "mqls": 24, "mqls_ly": 6,
            "addr_leads": 10, "addr_leads_ly": 2, "addr_rate": 42, "addr_rate_ly": 33,
            "close_won": 20, "close_won_ly": 0, "agpv": 29660000, "agpv_ly": 3000000,
            "agpv_per_lead": 2.97, "agpv_per_lead_ly": 1.50,
        },
        "midmarket": {
            "name": "Mid-Market", "leads": 5, "leads_ly": 0, "mqls": 5, "mqls_ly": 0,
            "addr_leads": 1, "addr_leads_ly": 0, "addr_rate": 25, "addr_rate_ly": None,
            "close_won": 0, "close_won_ly": None, "agpv": 140000000, "agpv_ly": 0,
            "agpv_per_lead": 140, "agpv_per_lead_ly": None,
        },
    },
    "table_rows": [
        {"segment": "Small", "leads_ly": 145, "leads_ty": 355, "yoy": "+145%", "mqls_ly": 145, "mqls_ty": 355, "addr_ly": 42, "addr_ty": 167, "addr_rate": "47%"},
        {"segment": "Medium", "leads_ly": 42, "leads_ty": 130, "yoy": "+210%", "mqls_ly": 42, "mqls_ty": 130, "addr_ly": 15, "addr_ty": 52, "addr_rate": "40%"},
        {"segment": "Premium", "leads_ly": 6, "leads_ty": 24, "yoy": "+300%", "mqls_ly": 6, "mqls_ty": 24, "addr_ly": 2, "addr_ty": 10, "addr_rate": "42%"},
        {"segment": "Mid-Market", "leads_ly": 0, "leads_ty": 5, "yoy": "New", "mqls_ly": 0, "mqls_ty": 5, "addr_ly": 0, "addr_ty": 1, "addr_rate": "25%"},
    ],
    "funnel": {
        "ty": {"leads": 514, "mqls": 514, "addr_leads": 230, "addr_rate": 45, "close_won": 5.65},
        "ly": {"leads": 193, "mqls": 193, "addr_leads": 59, "addr_rate": 42, "close_won": 1.69},
    },
    "donut": {
        "leads": {"Small": 355, "Medium": 130, "Premium": 24, "Mid-Market": 5},
        "agpv": {"Small": 9.74, "Medium": 18.85, "Premium": 29.66, "Mid-Market": 140},
    },
}

# ======================================================================
# SQL template
# TODO: Replace table reference with your actual Snowflake table
# ======================================================================

_FETCH_SQL = f"""
SELECT
    segment,
    COUNT(*)                                              AS leads,
    SUM(CASE WHEN is_mql THEN 1 ELSE 0 END)              AS mqls,
    SUM(CASE WHEN is_addressable THEN 1 ELSE 0 END)      AS addr_leads,
    ROUND(100.0 * SUM(CASE WHEN is_addressable THEN 1 ELSE 0 END)
          / NULLIF(COUNT(*), 0), 2)                       AS addr_rate,
    ROUND(100.0 * SUM(CASE WHEN close_won_28d THEN 1 ELSE 0 END)
          / NULLIF(SUM(CASE WHEN is_addressable THEN 1 ELSE 0 END), 0), 2) AS close_won,
    COALESCE(SUM(addressable_agpv), 0)                    AS agpv
FROM
    {config.B2B_LEADS_TABLE}
WHERE
    lead_date BETWEEN %(start_date)s AND %(end_date)s
GROUP BY segment
ORDER BY leads DESC
"""


class B2BDemandGenEngine:
    """Data engine powering the B2B Demand Gen dashboard."""

    def __init__(self, client: SnowflakeClient) -> None:
        self._client = client

    def fetch_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Fetch B2B data from Snowflake for the given date range + LY comparison."""
        logger.info("Fetching B2B data for %s → %s", start_date, end_date)

        cy_rows = self._client.execute_query(_FETCH_SQL, {"start_date": start_date, "end_date": end_date})

        ly_start = _shift_date(start_date, -365)
        ly_end = _shift_date(end_date, -365)
        ly_rows = self._client.execute_query(_FETCH_SQL, {"start_date": ly_start, "end_date": ly_end})

        return self._build_payload(cy_rows, ly_rows, start_date, end_date, ly_start, ly_end)

    def generate_insights(self, data: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
        """Auto-generate wins and watchouts from segment data.

        Returns dict with 'wins' and 'watchouts' lists, each item having
        'text' and optionally 'severity' ('amber' for watchouts).
        """
        wins: List[Dict[str, str]] = []
        watchouts: List[Dict[str, str]] = []
        segments = data.get("segments", {})
        total_leads = sum(s.get("leads", 0) for s in segments.values())

        for key, seg in segments.items():
            name = seg.get("name", key)
            leads = seg.get("leads", 0)
            leads_ly = seg.get("leads_ly", 0)
            mqls = seg.get("mqls", 0)
            close_won = seg.get("close_won", 0)
            close_won_ly = seg.get("close_won_ly")
            agpv = seg.get("agpv", 0)
            agpv_ly = seg.get("agpv_ly", 0)
            addr_rate = seg.get("addr_rate", 0)
            addr_rate_ly = seg.get("addr_rate_ly")

            # New segment — no LY baseline
            if leads_ly == 0 and leads > 0:
                watchouts.append({"text": f"{name} segment has near-zero historical baseline — hard to benchmark", "severity": "amber"})
                if close_won == 0 and leads > 0:
                    watchouts.append({"text": f"{name} 28D Close Won at 0% — no conversions yet", "severity": "red"})
                continue

            # MQL growth > 100%
            mql_change = pct_change(leads_ly, mqls)
            if mql_change is not None and mql_change > 100:
                wins.append({"text": f"{name} MQLs exploded +{mql_change:.0f}% YoY ({leads_ly} → {mqls})"})

            # Close-won drop > 20%
            if close_won_ly and close_won_ly > 0:
                cw_change = pct_change(close_won_ly, close_won)
                if cw_change is not None and cw_change < -20:
                    watchouts.append({"text": f"{name} 28D Close Won dropped {cw_change:+.0f}% YoY ({close_won_ly}% → {close_won}%)", "severity": "red"})

            # 0% conversion with leads
            if close_won == 0 and leads > 0 and (close_won_ly is None or close_won_ly == 0):
                pass  # Already covered by new segment
            elif close_won == 0 and leads > 0:
                watchouts.append({"text": f"{name} 28D Close Won at 0% — no conversions yet", "severity": "red"})

            # Close-won from 0 to positive = win
            if (close_won_ly is not None and close_won_ly == 0) and close_won > 0:
                wins.append({"text": f"{name} 28D Close Won hit {close_won}% (from 0% last year)"})

            # Addressability improvement > 5pp
            if addr_rate_ly is not None:
                pp = addr_rate - addr_rate_ly
                if pp > 5:
                    wins.append({"text": f"{name} addressability rate improved +{pp:.0f}pp ({addr_rate_ly}% → {addr_rate}%)"})

            # aGPV growth
            if agpv_ly > 0:
                agpv_change = pct_change(agpv_ly, agpv)
                if agpv_change is not None and agpv_change > 200:
                    wins.append({"text": f"{name} aGPV surged +{agpv_change:.0f}% ({format_currency(agpv_ly)} → {format_currency(agpv)})"})

            # aGPV per lead growth > 100%
            if leads > 0 and leads_ly > 0 and agpv_ly > 0:
                apl_cy = agpv / leads
                apl_ly = agpv_ly / leads_ly
                apl_change = pct_change(apl_ly, apl_cy)
                if apl_change is not None and apl_change > 100:
                    wins.append({"text": f"Addressable aGPV per Lead up {apl_change:.0f}% ({format_currency(apl_ly)} → {format_currency(apl_cy)})"})

            # Segment concentration risk
            if total_leads > 0 and (leads / total_leads * 100) > config.ALERT_THRESHOLDS["segment_concentration_pct"]:
                watchouts.append({"text": f"{name} segment dominates lead mix at {leads / total_leads * 100:.0f}% — concentration risk?", "severity": "amber"})

        # Addressable leads overall
        kpis = {k["label"]: k for k in data.get("kpis", [])}
        addr_kpi = kpis.get("Addressable Leads", {})
        if addr_kpi.get("ly_value", 0) > 0:
            addr_change = pct_change(addr_kpi["ly_value"], addr_kpi["value"])
            if addr_change and addr_change > 200:
                wins.append({"text": f"Addressable Leads nearly {addr_kpi['value'] / addr_kpi['ly_value']:.0f}x'd — {addr_kpi['ly_value']} → {addr_kpi['value']} ({addr_change:+.0f}%)"})

        return {"wins": wins, "watchouts": watchouts}

    def get_dashboard_payload(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """Return complete JSON-ready dashboard payload. Falls back on Snowflake failure."""
        if not end_date:
            end_date = datetime.utcnow().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=5)).strftime("%Y-%m-%d")

        try:
            self._client.connect()
            data = self.fetch_data(start_date, end_date)
            self._client.disconnect()
            source = "snowflake"
            logger.info("B2B data fetched from Snowflake.")
        except Exception as exc:
            logger.warning("Snowflake unavailable (%s). Using fallback data.", exc)
            data = FALLBACK_DATA
            source = "fallback"

        insights = self.generate_insights(data)

        return {
            "data": data,
            "insights": insights,
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "source": source,
        }

    @staticmethod
    def _build_payload(cy_rows, ly_rows, start, end, ly_start, ly_end) -> Dict[str, Any]:
        """Transform raw Snowflake rows into structured dashboard dict."""
        ly_map = {r["SEGMENT"]: r for r in ly_rows}
        segments = {}
        totals = {"leads": 0, "mqls": 0, "addr": 0, "agpv": 0, "leads_ly": 0, "mqls_ly": 0, "addr_ly": 0, "agpv_ly": 0}

        for row in cy_rows:
            seg = row["SEGMENT"]
            ly = ly_map.get(seg, {})
            s = {
                "name": seg, "leads": int(row.get("LEADS", 0)), "leads_ly": int(ly.get("LEADS", 0)),
                "mqls": int(row.get("MQLS", 0)), "mqls_ly": int(ly.get("MQLS", 0)),
                "addr_leads": int(row.get("ADDR_LEADS", 0)), "addr_leads_ly": int(ly.get("ADDR_LEADS", 0)),
                "addr_rate": float(row.get("ADDR_RATE", 0) or 0),
                "addr_rate_ly": float(ly.get("ADDR_RATE", 0) or 0) if ly else None,
                "close_won": float(row.get("CLOSE_WON", 0) or 0),
                "close_won_ly": float(ly.get("CLOSE_WON", 0) or 0) if ly else None,
                "agpv": float(row.get("AGPV", 0) or 0), "agpv_ly": float(ly.get("AGPV", 0) or 0),
            }
            segments[seg.lower().replace("-", "").replace(" ", "")] = s
            for k in ("leads", "mqls", "addr", "agpv"):
                totals[k] += s.get(k if k != "addr" else "addr_leads", 0)
                totals[f"{k}_ly"] += s.get(f"{k if k != 'addr' else 'addr_leads'}_ly", 0)

        kpis = [
            _make_kpi("Total Leads", totals["leads"], totals["leads_ly"]),
            _make_kpi("Total MQLs", totals["mqls"], totals["mqls_ly"]),
            _make_kpi("Addressable Leads", totals["addr"], totals["addr_ly"]),
        ]

        return {"period": {"start": start, "end": end, "ly_start": ly_start, "ly_end": ly_end},
                "kpis": kpis, "segments": segments}


def _make_kpi(label, val, ly_val, unit=""):
    change = pct_change(ly_val, val)
    return {"label": label, "value": val, "ly_value": ly_val,
            "yoy_pct": change, "yoy_label": format_pct_change(ly_val, val),
            "dir": "up" if (change or 0) > 0 else "down" if (change or 0) < 0 else "neutral", "unit": unit}


def _shift_date(iso: str, days: int) -> str:
    return (datetime.strptime(iso, "%Y-%m-%d") + timedelta(days=days)).strftime("%Y-%m-%d")
