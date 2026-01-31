"""Main CLI entry point for agent-brain CLI.

This module provides the command-line interface for managing and querying
the Agent Brain RAG server. The primary entry point is `agent-brain`,
with `doc-svr-ctl` provided for backward compatibility.
"""

import sys
import warnings

import click

from . import __version__
from .commands import (
    index_command,
    init_command,
    list_command,
    query_command,
    reset_command,
    start_command,
    status_command,
    stop_command,
)


@click.group()
@click.version_option(version=__version__, prog_name="agent-brain")
def cli() -> None:
    """Agent Brain CLI - Manage and query the Agent Brain RAG server.

    A command-line interface for interacting with the Agent Brain document
    indexing and semantic search API.

    \b
    Project Commands:
      init     Initialize a new agent-brain project
      start    Start the server for this project
      stop     Stop the server for this project
      list     List all running agent-brain instances

    \b
    Server Commands:
      status   Check server status
      query    Search documents
      index    Index documents from a folder
      reset    Clear all indexed documents

    \b
    Examples:
      agent-brain init                      # Initialize project
      agent-brain start                     # Start server
      agent-brain status                    # Check server status
      agent-brain query "how to use python" # Search documents
      agent-brain index ./docs              # Index documents
      agent-brain stop                      # Stop server

    \b
    Environment Variables:
      DOC_SERVE_URL  Server URL (default: http://127.0.0.1:8000)
    """
    pass


def cli_deprecated() -> None:
    """Deprecated entry point for doc-svr-ctl command.

    Shows a deprecation warning and then runs the main CLI.
    """
    warnings.warn(
        "\n"
        "WARNING: 'doc-svr-ctl' is deprecated and will be removed in v2.0.\n"
        "Please use 'agent-brain' instead.\n"
        "\n"
        "Migration guide: docs/MIGRATION.md\n"
        "Online: https://github.com/SpillwaveSolutions/agent-brain/blob/main/docs/MIGRATION.md\n",
        DeprecationWarning,
        stacklevel=1,
    )
    # Print to stderr for visibility since warnings may be filtered
    print(
        "\033[93mWARNING: 'doc-svr-ctl' is deprecated. "
        "Use 'agent-brain' instead. See docs/MIGRATION.md\033[0m",
        file=sys.stderr,
    )
    cli()


# Register project management commands
cli.add_command(init_command, name="init")
cli.add_command(start_command, name="start")
cli.add_command(stop_command, name="stop")
cli.add_command(list_command, name="list")

# Register server interaction commands
cli.add_command(status_command, name="status")
cli.add_command(query_command, name="query")
cli.add_command(index_command, name="index")
cli.add_command(reset_command, name="reset")


if __name__ == "__main__":
    cli()
