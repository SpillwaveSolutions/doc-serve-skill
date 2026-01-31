#!/usr/bin/env python3
"""
Wait for doc-serve server to reach a specific health status.

Usage:
    python wait_for_health.py [--status healthy] [--timeout 60]

Exit codes:
    0: Desired status reached
    1: Timeout reached
    2: Server unreachable
"""

import argparse
import sys
import time
import subprocess
import json
from pathlib import Path

# Add parent to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.e2e_config import CLI_DIR, HEALTH_POLL_INTERVAL


def run_cli_command(*args, timeout: int = 10) -> dict:
    """Run a CLI command and return result."""
    try:
        result = subprocess.run(
            ["poetry", "run", "agent-brain", *args],
            cwd=CLI_DIR,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"returncode": -1, "stdout": "", "stderr": "Command timed out"}
    except Exception as e:
        return {"returncode": -1, "stdout": "", "stderr": str(e)}


def get_server_status() -> dict:
    """Get current server status."""
    result = run_cli_command("status", "--json")
    if result["returncode"] == 0:
        try:
            return json.loads(result["stdout"])
        except json.JSONDecodeError:
            return {}
    return {}


def wait_for_status(
    target_status: str = "healthy",
    timeout: int = 60,
    interval: float = HEALTH_POLL_INTERVAL
) -> int:
    """Wait for server to reach target status."""
    start = time.time()
    last_status = None

    while time.time() - start < timeout:
        status_data = get_server_status()
        current_status = status_data.get("health", {}).get("status")

        if current_status != last_status:
            print(f"Current status: {current_status}")
            last_status = current_status

        if current_status == target_status:
            print(f"Target status '{target_status}' reached!")
            return 0

        # If waiting for healthy and already past indexing
        if target_status == "healthy" and current_status == "healthy":
            return 0

        # If waiting for indexing completion
        if target_status == "healthy" and current_status == "indexing":
            indexing = status_data.get("indexing", {})
            progress = indexing.get("progress_percent", 0)
            print(f"  Indexing progress: {progress:.1f}%")

        time.sleep(interval)

    print(f"Timeout: did not reach '{target_status}' within {timeout}s")
    return 1


def main():
    parser = argparse.ArgumentParser(description="Wait for server health status")
    parser.add_argument(
        "--status", "-s",
        default="healthy",
        choices=["healthy", "indexing", "degraded"],
        help="Target status to wait for (default: healthy)"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=60,
        help="Maximum time to wait in seconds (default: 60)"
    )
    parser.add_argument(
        "--interval", "-i",
        type=float,
        default=HEALTH_POLL_INTERVAL,
        help=f"Polling interval in seconds (default: {HEALTH_POLL_INTERVAL})"
    )

    args = parser.parse_args()
    sys.exit(wait_for_status(args.status, args.timeout, args.interval))


if __name__ == "__main__":
    main()
