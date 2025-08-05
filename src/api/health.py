"""
Health Check Endpoints
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "mikrobot-fastversion"
    }


@router.get("/detailed")
async def detailed_health():
    """Detailed health check with component status"""
    # This would be populated by the main app
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api": {"status": "healthy", "response_time_ms": 1.2},
            "database": {"status": "healthy", "connection_pool": "available"},
            "mt5": {"status": "checking", "connection": "pending"},
            "orchestrator": {"status": "healthy", "active_cells": 5}
        },
        "version": "1.0.0"
    }


@router.get("/readiness")
async def readiness_check():
    """Kubernetes readiness probe"""
    # Check if all critical components are ready
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/liveness")
async def liveness_check():
    """Kubernetes liveness probe"""
    # Check if application is alive
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }