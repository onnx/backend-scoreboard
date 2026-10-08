# SPDX-License-Identifier: Apache-2.0

"""Tests for the shared backend subprocess runner.

Run with ``pytest --noconftest -o pythonpath=backends test/test_subprocess_runner.py``
so that the backend-suite conftest is not loaded.
"""

import os
import signal
import time

import pytest
from onnx.backend.test.runner import BackendIsNotSupposedToImplementIt
from subprocess_runner import WorkerError, run_in_subprocess

# Larger than any OS pipe buffer, so the parent must read before joining.
LARGE_RESULT_BYTES = 32 * 1024 * 1024
TIMED_OUT = "demo process timed out"


def _double(value):
    return [value * 2]


def _large_result():
    return [b"x" * LARGE_RESULT_BYTES]


def _raise_worker_error():
    raise WorkerError("unsupported op")


def _crash():
    os._exit(3)


def _exit_nonzero_after_result():
    import atexit

    atexit.register(os._exit, 7)
    return ["done"]


def _hang():
    time.sleep(60)


def _ignore_sigterm_and_hang():
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
    time.sleep(60)


def _run(target, args=(), timeout=30):
    return run_in_subprocess(target, args, timeout=timeout, name="demo")


def test_returns_worker_result():
    """Return the value computed by the worker."""
    assert _run(_double, (21,)) == [42]


def test_returns_result_larger_than_pipe_buffer():
    """Deliver a result that would deadlock a join-before-read parent."""
    (result,) = _run(_large_result)
    assert len(result) == LARGE_RESULT_BYTES


def test_worker_error_skips_with_message():
    """Turn a WorkerError raised by the worker into a skip with its message."""
    with pytest.raises(BackendIsNotSupposedToImplementIt, match="unsupported op"):
        _run(_raise_worker_error)


def test_crash_without_result_is_reported_as_crash():
    """Report a worker that dies without sending a result as crashed."""
    with pytest.raises(
        BackendIsNotSupposedToImplementIt, match=r"demo process crashed \(exit code 3\)"
    ):
        _run(_crash)


def test_result_is_kept_when_worker_exits_nonzero_afterwards():
    """Keep a delivered result even if the worker exits non-zero afterwards."""
    assert _run(_exit_nonzero_after_result) == ["done"]


def test_timeout_is_reported():
    """Stop a hanging worker and report a timeout."""
    start = time.monotonic()
    with pytest.raises(BackendIsNotSupposedToImplementIt, match=TIMED_OUT):
        _run(_hang, timeout=1)
    assert time.monotonic() - start < 30


def test_worker_ignoring_sigterm_is_killed():
    """Escalate to kill() when the worker ignores terminate()."""
    start = time.monotonic()
    with pytest.raises(BackendIsNotSupposedToImplementIt, match=TIMED_OUT):
        _run(_ignore_sigterm_and_hang, timeout=1)
    # 1 s timeout + 5 s grace period after terminate(), far below the 60 s sleep.
    assert time.monotonic() - start < 30
