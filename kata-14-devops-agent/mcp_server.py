#!/usr/bin/env python3
"""
Kata 14: Custom MCP Server for AWS DevOps Agent

This MCP server exposes internal operations tools that AWS DevOps Agent calls
when investigating incidents. DevOps Agent discovers your tools via the MCP
protocol and invokes them during incident investigations.

IMPORTANT — Transport protocol:
    AWS DevOps Agent requires the Streamable HTTP MCP transport protocol.
    This server uses FastMCP (from the `mcp` package) which implements the
    correct protocol. Do NOT use a plain REST server (like kata-07's HTTP server)
    — DevOps Agent will not be able to communicate with it.

Usage:
    export MCP_API_KEY=kata14-dev-key
    python mcp_server.py
    # Server starts on http://localhost:8001/mcp

To expose publicly so DevOps Agent can reach it:
    ngrok http 8001
    # Register the ngrok URL in: AWS Console > DevOps Agent > MCP Servers
    # OR via CLI: aws devopsagent register-service --service mcpserver ...

The tools return mock data for development. In production, replace the mock
data dictionaries with real calls to your deployment pipeline, runbook system,
and on-call scheduling service.

Registration fields (used when registering this server with DevOps Agent):
    - Endpoint URL: https://your-ngrok-url.ngrok.io/mcp   (Streamable HTTP)
    - Auth type: API Key
    - API Key Header: X-Api-Key
    - API Key Name: kata14-mcp-key
    - API Key Value: kata14-dev-key   (must match MCP_API_KEY env var)
"""

import json
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

MCP_PORT = int(os.getenv("MCP_PORT", 8001))
MCP_API_KEY = os.getenv("MCP_API_KEY", "kata14-dev-key")

# ==============================================================================
# FastMCP server — uses Streamable HTTP transport (required by DevOps Agent)
# ==============================================================================

mcp = FastMCP(
    name="devops-agent-tools",
    description="Internal operations tools for AWS DevOps Agent incident investigations"
)

# ==============================================================================
# Mock data — replace with real data sources in production
# ==============================================================================

MOCK_DEPLOYMENTS = {
    "payment-api": [
        {
            "version": "v2.4.1",
            "hours_ago": 2,
            "deployed_by": "alice@example.com",
            "commit": "a1b2c3d",
            "status": "success",
            "changes": ["Updated payment gateway timeout from 10s to 5s", "Fixed retry logic"]
        },
        {
            "version": "v2.4.0",
            "hours_ago": 26,
            "deployed_by": "bob@example.com",
            "commit": "e4f5g6h",
            "status": "success",
            "changes": ["Added new card validation endpoint", "Updated dependencies"]
        }
    ],
    "auth-service": [
        {
            "version": "v1.9.3",
            "hours_ago": 48,
            "deployed_by": "charlie@example.com",
            "commit": "i7j8k9l",
            "status": "success",
            "changes": ["Patched JWT library CVE-2024-1234", "Increased session timeout"]
        }
    ],
    "inventory-service": []
}

MOCK_RUNBOOKS = {
    "high_latency": {
        "steps": [
            "1. Check CloudWatch metrics: P99 latency, request rate, error rate",
            "2. Review recent deployments in the past 2 hours (use get_deployment_history)",
            "3. Check database connection pool saturation",
            "4. Review downstream service health (dependencies)",
            "5. If latency > 5s for > 5 min: page on-call via get_team_oncall",
            "6. Initiate rollback if recent deployment is the likely cause"
        ],
        "escalation_minutes": 15
    },
    "db_connection_failure": {
        "steps": [
            "1. Verify RDS instance status in AWS Console",
            "2. Check security group rules — port 5432/3306 must be open from app subnet",
            "3. Verify connection string in Secrets Manager has not been rotated",
            "4. Check max_connections parameter — may need to increase",
            "5. Restart application connection pool (rolling restart if possible)",
            "6. If RDS is down: trigger failover to read replica"
        ],
        "escalation_minutes": 5
    },
    "memory_leak": {
        "steps": [
            "1. Capture heap dump before restarting (use: kill -3 <pid>)",
            "2. Check for unbounded caches or growing queues in metrics",
            "3. Review recent code changes for missing cleanup / close() calls",
            "4. Rolling restart of affected instances to restore service",
            "5. Open incident ticket with heap dump attached",
            "6. Monitor memory trend after restart — schedule fix in next sprint"
        ],
        "escalation_minutes": 30
    },
    "cpu_spike": {
        "steps": [
            "1. Identify top CPU-consuming processes: top / pidstat",
            "2. Check if spike correlates with a traffic increase or cron job",
            "3. Profile with py-spy (Python) or async-profiler (JVM)",
            "4. Check for infinite loops or tight retry loops in recent deployments",
            "5. If CPU > 95% for > 10 min: page on-call",
            "6. Auto-scaling should kick in — verify ASG policy is active"
        ],
        "escalation_minutes": 20
    },
    "default": {
        "steps": [
            "1. Identify the affected service and scope of impact",
            "2. Check recent deployments for the affected service",
            "3. Review CloudWatch logs and metrics for anomalies",
            "4. Determine if this is a known incident pattern",
            "5. Page on-call if service is degraded for more than 10 minutes",
            "6. Document findings in incident ticket"
        ],
        "escalation_minutes": 10
    }
}

MOCK_ONCALL = {
    "payment-api": {
        "name": "Alice Johnson",
        "contact": "alice@example.com | Slack: @alice | PagerDuty: +1-555-0101",
        "timezone": "US/Pacific"
    },
    "auth-service": {
        "name": "Bob Smith",
        "contact": "bob@example.com | Slack: @bob | PagerDuty: +1-555-0102",
        "timezone": "Europe/London"
    },
    "default": {
        "name": "Platform On-Call",
        "contact": "platform-oncall@example.com | Slack: #platform-alerts | PagerDuty: +1-555-0100",
        "timezone": "US/Eastern"
    }
}

# ==============================================================================
# MCP tools — DevOps Agent discovers and calls these during investigations
# ==============================================================================

@mcp.tool()
def get_deployment_history(service: str, hours: int = 24) -> str:
    """Return recent deployments for a service within the last N hours.

    Use this to check whether a recent deployment could have caused the incident.
    Check deployments in the past 2-4 hours first, then expand the window.

    Args:
        service: Service name (e.g., "payment-api", "auth-service", "inventory-service")
        hours: Look-back window in hours (default: 24)
    """
    all_deployments = MOCK_DEPLOYMENTS.get(service, [])
    recent = [d for d in all_deployments if d["hours_ago"] <= hours]

    return json.dumps({
        "service": service,
        "window_hours": hours,
        "count": len(recent),
        "deployments": recent,
        "note": "Replace MOCK_DEPLOYMENTS with your real deployment pipeline API"
    }, indent=2)


@mcp.tool()
def query_runbook(incident_type: str) -> str:
    """Return runbook steps for a given incident type.

    Retrieves the standard operating procedure (SOP) for handling a specific
    class of incident. Use this early in the investigation to follow the
    established protocol.

    Args:
        incident_type: Type of incident. Known types: high_latency,
            db_connection_failure, memory_leak, cpu_spike.
            Falls back to a generic runbook for unknown types.
    """
    runbook = MOCK_RUNBOOKS.get(incident_type, MOCK_RUNBOOKS["default"])
    matched = incident_type in MOCK_RUNBOOKS

    return json.dumps({
        "incident_type": incident_type,
        "matched_specific_runbook": matched,
        "steps": runbook["steps"],
        "escalation_threshold_minutes": runbook["escalation_minutes"],
        "note": "Replace MOCK_RUNBOOKS with your real runbook system API"
    }, indent=2)


@mcp.tool()
def get_team_oncall(service: str) -> str:
    """Return the current on-call engineer and contact info for a service.

    Use this when the investigation requires human escalation or when
    the agent needs to know who to notify about the incident.

    Args:
        service: Service name to look up on-call contact.
            Falls back to the platform on-call for unknown services.
    """
    oncall = MOCK_ONCALL.get(service, MOCK_ONCALL["default"])

    return json.dumps({
        "service": service,
        "oncall_engineer": oncall["name"],
        "contact": oncall["contact"],
        "timezone": oncall["timezone"],
        "as_of_utc": datetime.now(timezone.utc).isoformat(),
        "note": "Replace MOCK_ONCALL with your real on-call scheduling API"
    }, indent=2)


# ==============================================================================
# Main
# ==============================================================================

def main() -> None:
    print("=" * 60)
    print(" Kata 14: DevOps Agent MCP Server")
    print("=" * 60)
    print("\nTransport: Streamable HTTP (required by AWS DevOps Agent)")
    print(f"Tools: get_deployment_history, query_runbook, get_team_oncall")
    print(f"\nStarting on http://localhost:{MCP_PORT}/mcp")
    print("\nTo expose publicly for DevOps Agent:")
    print(f"  ngrok http {MCP_PORT}")
    print("  Register ngrok URL in: DevOps Agent console > MCP Servers")
    print("  OR via CLI: aws devopsagent register-service --service mcpserver ...")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 60)

    # FastMCP runs with Streamable HTTP transport (protocol required by DevOps Agent)
    mcp.run(transport="streamable-http", host="0.0.0.0", port=MCP_PORT)


if __name__ == "__main__":
    main()
