"""
Email notification module.

Sends HTML emails, alert digests, and staleness warnings via SMTP.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

import config

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Sends email notifications via SMTP."""

    def __init__(self) -> None:
        self.host = config.SMTP_HOST
        self.port = config.SMTP_PORT
        self.user = config.SMTP_USER
        self.password = config.SMTP_PASSWORD
        self.sender = config.EMAIL_FROM
        self.recipients = [r.strip() for r in config.EMAIL_RECIPIENTS.split(",") if r.strip()]

        if not self._is_configured():
            logger.warning("Email SMTP not configured. Email notifications will be skipped.")
        else:
            logger.info("EmailNotifier initialized.")

    def send_email(self, subject: str, body_html: str, recipients: Optional[List[str]] = None) -> bool:
        """Send an HTML email."""
        if not self._is_configured():
            logger.warning("SMTP not configured — skipping email.")
            return False
        to = recipients or self.recipients
        if not to:
            logger.warning("No recipients — skipping email.")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = ", ".join(to)
        msg.attach(MIMEText(body_html, "html"))

        try:
            with smtplib.SMTP(self.host, self.port, timeout=30) as server:
                server.ehlo()
                server.starttls()
                server.login(self.user, self.password)
                server.sendmail(self.sender, to, msg.as_string())
            logger.info("Email sent: '%s' → %s", subject, to)
            return True
        except Exception:
            logger.exception("Failed to send email.")
            return False

    def send_alert_digest(self, alerts: List[Dict[str, Any]], dashboard_name: str) -> bool:
        """Send a digest email with multiple alerts in an HTML table."""
        if not alerts:
            logger.info("No alerts for '%s' — skipping digest.", dashboard_name)
            return True

        severity_colors = {"critical": "#dc2626", "monitor": "#d97706", "opportunity": "#059669"}
        rows = ""
        for a in alerts:
            sev = a.get("severity", "info")
            color = severity_colors.get(sev, "#333")
            rows += f"""<tr>
                <td style="padding:10px;border:1px solid #e5e7eb;"><span style="color:{color};font-weight:700;">{sev.upper()}</span></td>
                <td style="padding:10px;border:1px solid #e5e7eb;font-weight:600;">{_esc(a.get('title',''))}</td>
                <td style="padding:10px;border:1px solid #e5e7eb;">{_esc(a.get('body',''))}</td>
                <td style="padding:10px;border:1px solid #e5e7eb;font-weight:500;">{_esc(a.get('action',''))}</td>
            </tr>"""

        html = f"""<html><body style="font-family:Inter,Arial,sans-serif;color:#1a1a2e;max-width:800px;margin:0 auto;">
        <h2 style="color:#0d9488;">🚨 Alert Digest — {_esc(dashboard_name)}</h2>
        <p>{len(alerts)} alert(s) detected during the latest refresh.</p>
        <table style="border-collapse:collapse;width:100%;font-size:13px;">
            <thead><tr style="background:#f1f5f9;">
                <th style="padding:10px;border:1px solid #e5e7eb;text-align:left;">Severity</th>
                <th style="padding:10px;border:1px solid #e5e7eb;text-align:left;">Title</th>
                <th style="padding:10px;border:1px solid #e5e7eb;text-align:left;">Details</th>
                <th style="padding:10px;border:1px solid #e5e7eb;text-align:left;">Action</th>
            </tr></thead>
            <tbody>{rows}</tbody>
        </table>
        <p style="margin-top:20px;font-size:11px;color:#94a3b8;">Automated message from Dashboard Backend · Made with ❤️ by Nick and Goose 🪿</p>
        </body></html>"""

        subject = f"🚨 [{dashboard_name}] {len(alerts)} Alert(s) — {_count_by_severity(alerts)}"
        logger.info("Sending alert digest for '%s' (%d alerts).", dashboard_name, len(alerts))
        return self.send_email(subject, html)

    def send_staleness_warning(self, dashboard_name: str, days_stale: int) -> bool:
        """Send a staleness warning email."""
        html = f"""<html><body style="font-family:Inter,Arial,sans-serif;color:#1a1a2e;">
        <h2 style="color:#dc2626;">⚠️ Stale Data Warning</h2>
        <p>The <strong>{_esc(dashboard_name)}</strong> dashboard has not been refreshed in <strong>{days_stale} day(s)</strong>.</p>
        <p>Please investigate the data pipeline and Snowflake connectivity.</p>
        <p style="margin-top:20px;font-size:11px;color:#94a3b8;">Automated message from Dashboard Backend</p>
        </body></html>"""
        return self.send_email(f"⚠️ Stale Data — {dashboard_name} ({days_stale} days)", html)

    def _is_configured(self) -> bool:
        return all([self.host, self.user, self.password, self.sender])


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _count_by_severity(alerts: List[Dict[str, Any]]) -> str:
    counts: Dict[str, int] = {}
    for a in alerts:
        s = a.get("severity", "info")
        counts[s] = counts.get(s, 0) + 1
    return ", ".join(f"{v} {k}" for k, v in counts.items())
