"""
Configuration module for the Dashboard Backend.

Loads settings from environment variables with fallback placeholder values.
All placeholder values are marked with TODO comments for easy identification.
"""

import os
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# Snowflake Connection Settings
# TODO: Set these environment variables or update the defaults below.
# =============================================================================

SNOWFLAKE_ACCOUNT: str = os.getenv("SNOWFLAKE_ACCOUNT", "TODO_ACCOUNT")
SNOWFLAKE_USER: str = os.getenv("SNOWFLAKE_USER", "TODO_USER")
SNOWFLAKE_PASSWORD: str = os.getenv("SNOWFLAKE_PASSWORD", "TODO_PASSWORD")
SNOWFLAKE_WAREHOUSE: str = os.getenv("SNOWFLAKE_WAREHOUSE", "TODO_WAREHOUSE")
SNOWFLAKE_DATABASE: str = os.getenv("SNOWFLAKE_DATABASE", "TODO_DATABASE")
SNOWFLAKE_SCHEMA: str = os.getenv("SNOWFLAKE_SCHEMA", "TODO_SCHEMA")

# TODO: Replace with your actual Snowflake table references
B2B_LEADS_TABLE: str = os.getenv("B2B_LEADS_TABLE", "TODO_DB.TODO_SCHEMA.TODO_B2B_LEADS")
MONKS_CHANNEL_TABLE: str = os.getenv("MONKS_CHANNEL_TABLE", "TODO_DB.TODO_SCHEMA.TODO_CHANNEL_PERF")

# =============================================================================
# Slack Integration
# TODO: Create a webhook at https://api.slack.com/messaging/webhooks
# =============================================================================

SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")

# =============================================================================
# Email / SMTP Settings
# TODO: Set these for email alert digests
# =============================================================================

SMTP_HOST: str = os.getenv("SMTP_HOST", "")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = os.getenv("SMTP_USER", "")
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")
EMAIL_RECIPIENTS: str = os.getenv("EMAIL_RECIPIENTS", "")

# =============================================================================
# Dashboard Settings
# =============================================================================

REFRESH_HOUR: int = int(os.getenv("REFRESH_HOUR", "7"))
REFRESH_MINUTE: int = int(os.getenv("REFRESH_MINUTE", "0"))
STALENESS_THRESHOLD_DAYS: int = int(os.getenv("STALENESS_THRESHOLD_DAYS", "14"))
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))

# =============================================================================
# Alert Thresholds
# =============================================================================

ALERT_THRESHOLDS: Dict[str, Any] = {
    "lead_collapse_pct": -40,
    "cpl_explosion_threshold": 1000,
    "close_won_drop_pct": -30,
    "form_dropoff_pct": 70,
    "cpl_doubling_pct": 80,
    "ctr_decline_pct": -30,
    "lead_surge_pct": 50,
    "cpl_efficiency_threshold": 50,
    "cpl_efficiency_min_leads": 100,
    "mqls_explosion_pct": 100,
    "addressability_erosion_pct": 35,
    "segment_concentration_pct": 80,
}
