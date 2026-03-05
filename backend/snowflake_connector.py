"""
Snowflake connector module.

Provides a reusable client class with context-manager support,
query execution returning rows as dicts, and comprehensive logging.
"""

import logging
from typing import Any, Dict, List, Optional

import config

logger = logging.getLogger(__name__)


class SnowflakeClient:
    """Thin wrapper around snowflake-connector-python.

    Usage::
        with SnowflakeClient() as client:
            rows = client.execute_query("SELECT 1 AS n")
    """

    def __init__(self) -> None:
        self.account = config.SNOWFLAKE_ACCOUNT
        self.user = config.SNOWFLAKE_USER
        self.password = config.SNOWFLAKE_PASSWORD
        self.warehouse = config.SNOWFLAKE_WAREHOUSE
        self.database = config.SNOWFLAKE_DATABASE
        self.schema = config.SNOWFLAKE_SCHEMA
        self._conn: Any = None
        logger.debug("SnowflakeClient initialised (account=%s)", self.account)

    def connect(self) -> "SnowflakeClient":
        """Open a connection to Snowflake."""
        self._validate_credentials()
        try:
            import snowflake.connector
            logger.info("Connecting to Snowflake account=%s …", self.account)
            self._conn = snowflake.connector.connect(
                account=self.account,
                user=self.user,
                password=self.password,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema,
            )
            logger.info("Snowflake connection established.")
        except ImportError:
            raise RuntimeError(
                "snowflake-connector-python is not installed. "
                "Run: pip install snowflake-connector-python"
            )
        return self

    def disconnect(self) -> None:
        """Close the connection if open."""
        if self._conn is not None:
            try:
                self._conn.close()
                logger.info("Snowflake connection closed.")
            except Exception as exc:
                logger.warning("Error closing Snowflake connection: %s", exc)
            finally:
                self._conn = None

    @property
    def is_connected(self) -> bool:
        return self._conn is not None

    def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute SQL and return rows as list of dicts."""
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")
        logger.debug("Executing: %.120s …", sql.strip())
        cursor = self._conn.cursor()
        try:
            cursor.execute(sql, params or {})
            cols = [d[0] for d in cursor.description] if cursor.description else []
            rows = [dict(zip(cols, row)) for row in cursor.fetchall()]
            logger.debug("Returned %d row(s).", len(rows))
            return rows
        finally:
            cursor.close()

    def __enter__(self) -> "SnowflakeClient":
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.disconnect()

    def _validate_credentials(self) -> None:
        """Raise early if credentials are still TODO placeholders."""
        placeholders = [
            f for f in ("account", "user", "password", "warehouse", "database", "schema")
            if getattr(self, f, "").startswith("TODO")
        ]
        if placeholders:
            raise RuntimeError(
                f"Snowflake credentials have TODO placeholders for: {', '.join(placeholders)}. "
                "Set the corresponding env vars or update backend/config.py."
            )


def get_client() -> SnowflakeClient:
    """Factory function — returns a new (unconnected) SnowflakeClient."""
    return SnowflakeClient()
