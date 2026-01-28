"""CLI commands for doc-svr-ctl."""

from .index import index_command
from .init import init_command
from .list_cmd import list_command
from .query import query_command
from .reset import reset_command
from .start import start_command
from .status import status_command
from .stop import stop_command

__all__ = [
    "index_command",
    "init_command",
    "list_command",
    "query_command",
    "reset_command",
    "start_command",
    "status_command",
    "stop_command",
]
