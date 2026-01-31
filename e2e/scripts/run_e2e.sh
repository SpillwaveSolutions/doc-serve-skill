#!/bin/bash
# E2E Test Runner for CI/CD
# Usage: ./run_e2e.sh [--verbose]
# Exit codes: 0=success, 1=test failure, 2=setup failure, 3=indexing failure

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
E2E_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$E2E_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_ok() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse arguments
VERBOSE=""
PYTEST_ARGS="-v"

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE="--verbose"
            PYTEST_ARGS="-v -s"
            shift
            ;;
        --pytest)
            USE_PYTEST=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--verbose] [--pytest]"
            exit 1
            ;;
    esac
done

# Check for required environment variable
if [ -z "$OPENAI_API_KEY" ]; then
    log_error "OPENAI_API_KEY environment variable is not set"
    log_info "Please set OPENAI_API_KEY before running E2E tests"
    exit 2
fi

# Cleanup function
SERVER_PID=""
cleanup() {
    log_info "Cleaning up..."
    if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
        kill -TERM "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
}

trap cleanup EXIT

log_info "=============================================="
log_info "Doc-Serve E2E Integration Tests"
log_info "=============================================="

# Check dependencies
log_info "Checking dependencies..."

if ! command -v poetry &> /dev/null; then
    log_error "Poetry is not installed"
    exit 2
fi

# Install dependencies if needed
log_info "Installing server dependencies..."
cd "$PROJECT_ROOT/agent-brain-server"
poetry install --quiet

log_info "Installing CLI dependencies..."
cd "$PROJECT_ROOT/agent-brain-cli"
poetry install --quiet

# Run tests using Python script or pytest
if [ "$USE_PYTEST" = true ]; then
    log_info "Running tests with pytest..."

    # Start server in background
    log_info "Starting doc-serve server..."
    cd "$PROJECT_ROOT/agent-brain-server"
    poetry run doc-serve &
    SERVER_PID=$!

    # Wait for server health
    log_info "Waiting for server to be healthy..."
    cd "$PROJECT_ROOT/agent-brain-cli"
    for i in {1..30}; do
        if poetry run agent-brain status --json 2>/dev/null | grep -q '"status"'; then
            STATUS=$(poetry run agent-brain status --json 2>/dev/null | grep -o '"status": "[^"]*"' | head -1)
            if echo "$STATUS" | grep -qE '"healthy"|"indexing"'; then
                log_ok "Server is ready"
                break
            fi
        fi
        if [ $i -eq 30 ]; then
            log_error "Server failed to become healthy"
            exit 2
        fi
        sleep 1
    done

    # Run pytest
    cd "$E2E_DIR"
    if python -m pytest integration/ $PYTEST_ARGS --tb=short; then
        log_ok "All tests passed!"
        exit 0
    else
        log_error "Some tests failed"
        exit 1
    fi
else
    # Run using Python script
    log_info "Running tests with run_e2e.py..."
    cd "$E2E_DIR"
    python scripts/run_e2e.py $VERBOSE
    exit $?
fi
