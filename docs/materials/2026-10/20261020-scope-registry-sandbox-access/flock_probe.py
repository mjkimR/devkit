"""Run with a scratch directory argument on a local filesystem; no third-party dependencies."""
import fcntl
import os
import platform
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1])
root.mkdir(parents=True, exist_ok=True)
lock = root / ".lock"
writer = os.open(lock, os.O_CREAT | os.O_RDWR, 0o600)
reader = os.open(lock, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
try:
    fcntl.flock(writer, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        fcntl.flock(reader, fcntl.LOCK_SH | fcntl.LOCK_NB)
    except BlockingIOError:
        pass
    else:
        raise AssertionError("reader failed to exclude exclusive writer")
    fcntl.flock(writer, fcntl.LOCK_UN)
    fcntl.flock(reader, fcntl.LOCK_SH | fcntl.LOCK_NB)
    code = """
import fcntl, os, sys
fd = os.open(sys.argv[1], os.O_RDWR)
try:
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    sys.exit(0)
sys.exit(1)
"""
    subprocess.run([sys.executable, "-c", code, str(lock)], check=True)
    other = os.open(lock, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        fcntl.flock(other, fcntl.LOCK_SH | fcntl.LOCK_NB)
    finally:
        os.close(other)
    os.close(reader)
    reader = -1
    fcntl.flock(writer, fcntl.LOCK_EX | fcntl.LOCK_NB)
finally:
    if reader >= 0:
        os.close(reader)
    os.close(writer)
print(f"PASS {platform.system()} {platform.release()}: read-only shared flock excludes exclusive writer; concurrent readers; close releases lock")
