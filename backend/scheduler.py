"""
Daily scheduler for dashboard refresh + notifications.

Runs a daily job at a configurable time (default 7:00 AM) that:
1. Refreshes data from both engines
2. Checks for critical alerts
3. Sends Slack notifications for critical/monitor alerts
4. Sends email digest for critical alerts
5. Checks staleness and sends warnings

Also starts the FastAPI server via uvicorn.
"""

import logging
import sys
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler

import config
from notifications.email_notifier import EmailNotifier
from notifications.slack_notifier import SlackNotifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def daily_refresh() -> None:
    """Execute the daily data refresh and notification cycle."""
    logger.info("═══ Daily refresh started at %s ═══", datetime.now(timezone.utc).isoformat())

    # Step 1: Refresh data
    try:
        from server import _cache, refresh_all
        results = refresh_all()
        logger.info("Data refresh results: %s", results)
    except Exception:
        logger.exception("Data refresh failed!")
        return

    slack = SlackNotifier()
    email = EmailNotifier()

    # Step 2: Process B2B alerts
    b2b_data = _cache.get("b2b", {})
    b2b_insights = b2b_data.get("insights", {})
    b2b_watchouts = b2b_insights.get("watchouts", [])

    for w in b2b_watchouts:
        if isinstance(w, dict):
            severity = w.get("severity", "amber")
            if severity == "red":
                slack.send_alert({"severity": "critical", "title": "B2B Demand Gen", "body": w.get("text", ""), "action": "Review immediately."})

    # Step 3: Process Monks alerts
    monks_data = _cache.get("monks", {})
    monks_alerts = monks_data.get("alerts", [])
    critical_alerts = [a for a in monks_alerts if a.get("severity") == "critical"]
    monitor_alerts = [a for a in monks_alerts if a.get("severity") == "monitor"]

    for alert in critical_alerts + monitor_alerts:
        slack.send_alert(alert)

    # Step 4: Email digest for critical alerts
    if critical_alerts:
        email.send_alert_digest(critical_alerts, "Monks Biweekly")

    # Step 5: Send daily summaries
    b2b_summary = {}
    for kpi in b2b_data.get("data", {}).get("kpis", []):
        if isinstance(kpi, dict):
            label = kpi.get("label", "")
            val = kpi.get("value", "")
            yoy = kpi.get("yoy_label", "")
            b2b_summary[label] = f"{val} ({yoy} YoY)"
    if b2b_summary:
        slack.send_dashboard_summary("B2B Demand Gen", b2b_summary)

    monks_summary_data = monks_data.get("data", {}).get("summary", {})
    if monks_summary_data:
        slack.send_dashboard_summary("Monks Biweekly", {
            "Total Spend": f"${monks_summary_data.get('total_spend', 0):,.0f}",
            "Total Leads": str(monks_summary_data.get("total_leads", 0)),
            "Avg CPL": f"${monks_summary_data.get('avg_cpl', 0):.2f}",
            "Avg CTR": f"{monks_summary_data.get('avg_ctr', 0):.2f}%",
        })

    # Step 6: Staleness check
    for name, cache_key in [("B2B Demand Gen", "b2b"), ("Monks Biweekly", "monks")]:
        last_updated = _cache.get(cache_key, {}).get("last_updated", "")
        if last_updated:
            try:
                last_dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
                days_stale = (datetime.now(timezone.utc) - last_dt).days
                if days_stale > config.STALENESS_THRESHOLD_DAYS:
                    slack.send_staleness_warning(name, days_stale, config.STALENESS_THRESHOLD_DAYS)
                    email.send_staleness_warning(name, days_stale)
            except Exception:
                logger.warning("Could not parse last_updated for %s", name)

    logger.info("═══ Daily refresh complete ═══")


def start_scheduler(hour: int = None, minute: int = None) -> BackgroundScheduler:
    """Start the background scheduler."""
    h = hour if hour is not None else config.REFRESH_HOUR
    m = minute if minute is not None else config.REFRESH_MINUTE
    scheduler = BackgroundScheduler()
    scheduler.add_job(daily_refresh, "cron", hour=h, minute=m, id="daily_refresh")
    scheduler.start()
    logger.info("Scheduler started — daily refresh at %02d:%02d", h, m)
    return scheduler


def run_once() -> None:
    """Run a single refresh immediately (useful for testing)."""
    logger.info("Running one-time refresh…")
    daily_refresh()
    logger.info("One-time refresh complete.")


if __name__ == "__main__":
    import uvicorn

    if "--once" in sys.argv:
        run_once()
    else:
        scheduler = start_scheduler()
        try:
            uvicorn.run("server:app", host=config.API_HOST, port=config.API_PORT, reload=False)
        finally:
            scheduler.shutdown()
