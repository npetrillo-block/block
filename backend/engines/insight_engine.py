"""
Shared insight / commentary engine.

Utility functions for number formatting, percentage-change calculation,
and narrative generation used by both dashboard engines.
"""

from typing import Optional, Tuple


def format_number(n: float) -> str:
    """Smart-format a number: 1.2M, 45K, 1,234, etc."""
    abs_n = abs(n)
    sign = "-" if n < 0 else ""
    if abs_n >= 1_000_000_000:
        return f"{sign}{abs_n / 1_000_000_000:.1f}B"
    if abs_n >= 1_000_000:
        return f"{sign}{abs_n / 1_000_000:.1f}M"
    if abs_n >= 10_000:
        return f"{sign}{abs_n / 1_000:.0f}K"
    if abs_n >= 1_000:
        return f"{sign}{abs_n:,.0f}"
    if isinstance(n, float) and n != int(n):
        return f"{sign}{abs_n:.2f}"
    return f"{sign}{int(abs_n)}"


def format_currency(n: float) -> str:
    """Format as currency: $1.23M, $45.67K, $1,234, etc."""
    abs_n = abs(n)
    sign = "-" if n < 0 else ""
    if abs_n >= 1_000_000_000:
        return f"{sign}${abs_n / 1_000_000_000:.2f}B"
    if abs_n >= 1_000_000:
        return f"{sign}${abs_n / 1_000_000:.2f}M"
    if abs_n >= 1_000:
        return f"{sign}${abs_n:,.0f}"
    return f"{sign}${abs_n:.2f}"


def format_pct_change(old: float, new: float) -> str:
    """Return a formatted percentage change string like '+145%' or '-9%'."""
    if old == 0:
        return "New" if new > 0 else "—"
    pct = ((new - old) / abs(old)) * 100
    return f"{pct:+.0f}%"


def pct_change(old: float, new: float) -> Optional[float]:
    """Return raw percentage change or None if old is zero."""
    if old == 0:
        return None
    return round(((new - old) / abs(old)) * 100, 2)


def classify_change(pct: Optional[float]) -> Tuple[str, str]:
    """Classify a percentage change into direction and severity.

    Returns:
        Tuple of (direction, severity) where:
        - direction: 'up', 'down', or 'neutral'
        - severity: 'strong', 'moderate', 'mild', or 'neutral'
    """
    if pct is None:
        return ("neutral", "neutral")
    if pct > 50:
        return ("up", "strong")
    if pct > 10:
        return ("up", "moderate")
    if pct > 0:
        return ("up", "mild")
    if pct < -50:
        return ("down", "strong")
    if pct < -10:
        return ("down", "moderate")
    if pct < 0:
        return ("down", "mild")
    return ("neutral", "neutral")


def generate_b2b_narrative(data: dict) -> str:
    """Generate a 2-3 sentence B2B demand gen summary from data.

    Args:
        data: Dict with 'kpis' list and 'segments' dict.
    """
    kpis = {k["label"]: k for k in data.get("kpis", [])}

    leads = kpis.get("Total Leads", {})
    leads_val = leads.get("value", 0)
    leads_ly = leads.get("ly_value", 0)
    leads_yoy = leads.get("yoy_label", "N/A")

    addr = kpis.get("Addressable Leads", {})
    addr_val = addr.get("value", 0)
    addr_yoy = addr.get("yoy_label", "N/A")

    cw = kpis.get("28D Close Won Rate", {})
    cw_val = cw.get("value", 0)
    cw_yoy = cw.get("yoy_label", "N/A")

    agpv = kpis.get("Total Addr. aGPV", {})
    agpv_val = agpv.get("value", 0)
    agpv_yoy = agpv.get("yoy_label", "N/A")

    segments = data.get("segments", {})
    top_seg = max(segments.items(), key=lambda x: x[1].get("leads", 0), default=("N/A", {}))

    return (
        f"B2B demand generation delivered {format_number(leads_val)} total leads "
        f"({leads_yoy} YoY), with addressable leads reaching {format_number(addr_val)} "
        f"({addr_yoy} YoY). "
        f"The 28-day close-won rate stands at {cw_val}% ({cw_yoy} YoY), "
        f"driving total addressable aGPV to {format_currency(agpv_val)} ({agpv_yoy} YoY). "
        f"{top_seg[0]} leads the segment mix with {format_number(top_seg[1].get('leads', 0))} leads."
    )


def generate_monks_narrative(data: dict) -> str:
    """Generate an executive summary paragraph for the Monks Biweekly dashboard.

    Args:
        data: Dict with 'channels' list and 'summary' dict.
    """
    summary = data.get("summary", {})
    channels = data.get("channels", [])

    total_spend = summary.get("total_spend", 0)
    spend_change = summary.get("spend_change_pct", 0)
    total_impressions = summary.get("total_impressions", 0)
    total_clicks = summary.get("total_clicks", 0)
    total_leads = summary.get("total_leads", 0)
    avg_ctr = summary.get("avg_ctr", 0)
    avg_cpl = summary.get("avg_cpl", 0)
    prior_cpl = summary.get("prior_cpl", 0)

    channel_names = [c.get("name", "") for c in channels]
    channel_str = ", ".join(channel_names) if channel_names else "all channels"

    best_channel = min(channels, key=lambda c: c.get("cpl", float("inf")), default={})
    best_name = best_channel.get("name", "N/A")
    best_cpl = best_channel.get("cpl", 0)

    cpl_direction = "improved" if avg_cpl < prior_cpl else "increased"

    return (
        f"Global spend scaled to ~{format_currency(total_spend)} "
        f"({spend_change:+.0f}% vs prior period) across {channel_str}, "
        f"generating {format_number(total_impressions)} impressions and "
        f"{format_number(total_clicks)} clicks. "
        f"CTR held at {avg_ctr:.2f}%. "
        f"CPL {cpl_direction} from {format_currency(prior_cpl)} to {format_currency(avg_cpl)}. "
        f"{best_name} remains the strongest channel with a {format_currency(best_cpl)} CPL."
    )
