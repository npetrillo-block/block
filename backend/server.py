"""
FastAPI server — serves dashboard data as JSON.

Endpoints for B2B Demand Gen and Monks Biweekly dashboards,
with in-memory caching, health checks, and manual refresh.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import config
from engines.b2b_demand_gen import B2BDemandGenEngine, FALLBACK_DATA as B2B_FALLBACK
from engines.monks_biweekly import MonksBiweeklyEngine, FALLBACK_DATA as MONKS_FALLBACK
from snowflake_connector import get_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ── App Setup ──
app = FastAPI(title="Dashboard Backend", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-Memory Cache ──
CACHE_TTL = 3600  # 1 hour
_cache: Dict[str, Any] = {"b2b": None, "monks": None, "ts": None}


def _is_fresh() -> bool:
    return _cache["ts"] is not None and (time.time() - _cache["ts"]) < CACHE_TTL


def refresh_all(b2b_start=None, b2b_end=None, monks_start=None, monks_end=None) -> Dict[str, str]:
    """Refresh both dashboards. Falls back gracefully."""
    results = {}
    client = get_client()

    # B2B
    try:
        engine = B2BDemandGenEngine(client)
        _cache["b2b"] = engine.get_dashboard_payload(b2b_start, b2b_end)
        results["b2b_demand_gen"] = _cache["b2b"].get("source", "unknown")
    except Exception as exc:
        logger.error("B2B refresh failed: %s", exc)
        _cache["b2b"] = {"data": B2B_FALLBACK, "insights": {"wins": [], "watchouts": []},
                         "last_updated": datetime.utcnow().isoformat() + "Z", "source": "fallback"}
        results["b2b_demand_gen"] = "fallback"

    # Monks
    try:
        engine = MonksBiweeklyEngine(client)
        _cache["monks"] = engine.get_dashboard_payload(monks_start, monks_end)
        results["monks_biweekly"] = _cache["monks"].get("source", "unknown")
    except Exception as exc:
        logger.error("Monks refresh failed: %s", exc)
        _cache["monks"] = {"data": MONKS_FALLBACK, "alerts": MONKS_FALLBACK.get("alerts", []),
                           "exec_summary": MONKS_FALLBACK.get("exec_summary", ""),
                           "last_updated": datetime.utcnow().isoformat() + "Z", "source": "fallback"}
        results["monks_biweekly"] = "fallback"

    _cache["ts"] = time.time()
    logger.info("Refresh complete: %s", results)
    return results


# ── Startup ──
@app.on_event("startup")
async def startup():
    logger.info("Server starting — loading initial data.")
    refresh_all()


# ── Endpoints ──

@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat(), "cache_fresh": _is_fresh()}


@app.get("/api/b2b-demand-gen")
async def get_b2b(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    if start_date or end_date or not _is_fresh():
        refresh_all(b2b_start=start_date, b2b_end=end_date)
    return JSONResponse(content=_cache.get("b2b") or {"source": "fallback", "data": B2B_FALLBACK})


@app.get("/api/monks-biweekly")
async def get_monks(
    period_start: Optional[str] = Query(None),
    period_end: Optional[str] = Query(None),
):
    if period_start or period_end or not _is_fresh():
        refresh_all(monks_start=period_start, monks_end=period_end)
    return JSONResponse(content=_cache.get("monks") or {"source": "fallback", "data": MONKS_FALLBACK})


@app.get("/api/b2b-demand-gen/alerts")
async def b2b_alerts():
    if not _is_fresh():
        refresh_all()
    data = _cache.get("b2b", {})
    return JSONResponse(content={"dashboard": "B2B Demand Gen", "insights": data.get("insights", {})})


@app.get("/api/monks-biweekly/alerts")
async def monks_alerts():
    if not _is_fresh():
        refresh_all()
    data = _cache.get("monks", {})
    return JSONResponse(content={"dashboard": "Monks Biweekly", "alerts": data.get("alerts", [])})


@app.post("/api/refresh")
async def manual_refresh():
    logger.info("Manual refresh triggered.")
    results = refresh_all()
    return JSONResponse(content={"status": "refreshed", "details": results, "timestamp": datetime.now(timezone.utc).isoformat()})
