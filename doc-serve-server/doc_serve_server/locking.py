"""File-based locking for doc-serve instances."""

import fcntl
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

LOCK_FILE = "doc-serve.lock"
PID_FILE = "doc-serve.pid"

# Module-level storage for lock file descriptors
_lock_fds: dict[str, int] = {}


def acquire_lock(state_dir: Path) -> bool:
    """Acquire an exclusive lock for the state directory.

    Non-blocking. Returns immediately if lock cannot be acquired.

    Args:
        state_dir: Path to the state directory.

    Returns:
        True if lock acquired, False if already held.
    """
    state_dir.mkdir(parents=True, exist_ok=True)
    lock_path = state_dir / LOCK_FILE

    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_WRONLY)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

        # Write PID
        pid_path = state_dir / PID_FILE
        pid_path.write_text(str(os.getpid()))

        # Store fd for later release
        _lock_fds[str(state_dir)] = fd
        logger.info(f"Lock acquired: {lock_path}")
        return True

    except OSError:
        logger.warning(f"Lock already held: {lock_path}")
        return False


def release_lock(state_dir: Path) -> None:
    """Release the lock for the state directory.

    Args:
        state_dir: Path to the state directory.
    """
    lock_path = state_dir / LOCK_FILE

    fd = _lock_fds.pop(str(state_dir), None)
    if fd is not None:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
        except OSError:
            pass

    # Clean up files
    for fname in [LOCK_FILE, PID_FILE]:
        fpath = state_dir / fname
        if fpath.exists():
            try:
                fpath.unlink()
            except OSError:
                pass

    logger.info(f"Lock released: {lock_path}")


def read_pid(state_dir: Path) -> Optional[int]:
    """Read the PID from the PID file.

    Args:
        state_dir: Path to the state directory.

    Returns:
        PID value or None if file doesn't exist or is invalid.
    """
    pid_path = state_dir / PID_FILE
    if not pid_path.exists():
        return None
    try:
        return int(pid_path.read_text().strip())
    except (ValueError, OSError):
        return None


def is_stale(state_dir: Path) -> bool:
    """Check if the lock is stale (PID no longer alive).

    Args:
        state_dir: Path to the state directory.

    Returns:
        True if the lock is stale or no PID exists.
    """
    pid = read_pid(state_dir)
    if pid is None:
        return True
    try:
        os.kill(pid, 0)
        return False  # Process is alive
    except ProcessLookupError:
        return True  # Process is dead
    except PermissionError:
        return False  # Process exists but we can't signal it


def cleanup_stale(state_dir: Path) -> None:
    """Clean up stale lock and PID files.

    Only cleans up if the lock is determined to be stale.

    Args:
        state_dir: Path to the state directory.
    """
    if is_stale(state_dir):
        for fname in [LOCK_FILE, PID_FILE, "runtime.json"]:
            fpath = state_dir / fname
            if fpath.exists():
                try:
                    fpath.unlink()
                    logger.info(f"Cleaned stale file: {fpath}")
                except OSError:
                    pass
