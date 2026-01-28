"""Main CLI entry point for doc-svr-ctl."""

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
@click.version_option(version=__version__, prog_name="doc-svr-ctl")
def cli() -> None:
    """Doc-Serve CLI - Manage and query the Doc-Serve server.

    A command-line interface for interacting with the Doc-Serve document
    indexing and semantic search API.

    \b
    Project Commands:
      init     Initialize a new doc-serve project
      start    Start the server for this project
      stop     Stop the server for this project
      list     List all running doc-serve instances

    \b
    Server Commands:
      status   Check server status
      query    Search documents
      index    Index documents from a folder
      reset    Clear all indexed documents

    \b
    Examples:
      doc-svr-ctl init                      # Initialize project
      doc-svr-ctl start                     # Start server
      doc-svr-ctl status                    # Check server status
      doc-svr-ctl query "how to use python" # Search documents
      doc-svr-ctl index ./docs              # Index documents
      doc-svr-ctl stop                      # Stop server

    \b
    Environment Variables:
      DOC_SERVE_URL  Server URL (default: http://127.0.0.1:8000)
    """
    pass


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
