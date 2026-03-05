"""
Slack notification module.

Sends messages, alerts, dashboard summaries, and staleness warnings
to Slack via incoming webhooks.
"""

import logging
from typing import Any, Dict, List, Optional

import requests

import config

logger = logging.getLogger(__name__)

SEVERITY_EMOJI = {"critical": "🔴", "monitor": "🟡", "opportunity": "🟢", "info": "🔵"}


class SlackNotifier:
    """Sends notifications to Slack via incoming webhooks."""

    def __init__(self, webhook_url: Optional[str] = None) -> None:
        self.webhook_url = webhook_url or config.SLACK_WEBHOOK_URL
        if not self.webhook_url or "YOUR" in self.webhook_url or "TODO" in self.webhook_url:
            logger.warning("Slack webhook URL not configured. Notifications will be skipped.")
            self.webhook_url = None
        else:
            logger.info("SlackNotifier initialized.")

    def send_message(self, text: str, channel: Optional[str] = None) -> bool:
        """Send a plain text message."""
        if not self._check():
            return False
        payload: Dict[str, Any] = {"text": text}
        if channel:
            payload["channel"] = channel
        return self._post(payload)

    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """Send a richly-formatted alert using Slack Block Kit."""
        if not self._check():
            return False
        severity = alert.get("severity", "info")
        emoji = SEVERITY_EMOJI.get(severity, "ℹ️")
        title = alert.get("title", "Alert")
        body = alert.get("body", "")
        action = alert.get("action", "")

        blocks: List[Dict[str, Any]] = [
            {"type": "header", "text": {"type": "plain_text", "text": f"{emoji} [{severity.upper()}] {title}", "emoji": True}},
            {"type": "section", "text": {"type": "mrkdwn", "text": body}},
        ]
        if action:
            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": f"*Action:* {action}"}})
        blocks.append({"type": "divider"})

        logger.info("Sending Slack alert: %s — %s", severity, title)
        return self._post({"text": f"{emoji} [{severity.upper()}] {title}: {body}", "blocks": blocks})

    def send_dashboard_summary(self, dashboard_name: str, data: Dict[str, Any]) -> bool:
        """Send a daily summary with key metrics."""
        if not self._check():
            return False
        lines = "\n".join(f"• *{k}:* {v}" for k, v in data.items())
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": f"📊 Daily Summary — {dashboard_name}", "emoji": True}},
            {"type": "section", "text": {"type": "mrkdwn", "text": lines or "_No metrics._"}},
            {"type": "divider"},
        ]
        logger.info("Sending dashboard summary for '%s'.", dashboard_name)
        return self._post({"text": f"📊 Daily Summary — {dashboard_name}", "blocks": blocks})

    def send_staleness_warning(self, dashboard_name: str, days_stale: int, threshold: int) -> bool:
        """Send a staleness warning."""
        if not self._check():
            return False
        text = (
            f"⚠️ *Stale Data — {dashboard_name}*\n"
            f"Data hasn't been refreshed in *{days_stale} days* (threshold: {threshold} days).\n"
            f"Please investigate the data pipeline."
        )
        logger.warning("Sending staleness warning: %s (%d days)", dashboard_name, days_stale)
        return self._post({"text": text})

    def _check(self) -> bool:
        if not self.webhook_url:
            logger.warning("Slack not configured — skipping.")
            return False
        return True

    def _post(self, payload: Dict[str, Any]) -> bool:
        try:
            resp = requests.post(self.webhook_url, json=payload, timeout=10)
            if resp.ok:
                logger.debug("Slack message sent.")
                return True
            logger.error("Slack returned %s: %s", resp.status_code, resp.text)
            return False
        except requests.RequestException:
            logger.exception("Failed to send Slack notification.")
            return False
