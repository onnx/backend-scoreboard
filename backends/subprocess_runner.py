# SPDX-License-Identifier: Apache-2.0

"""Run backend inference in an isolated, spawned worker process.

Native runtimes can segfault, abort or hang on unsupported models. Running each
inference in a short-lived process confines such failures to a single test,
which is then reported as skipped instead of taking down the whole run.

Each runtime image copies this file next to its backend module, so backends
import it as the top-level module ``subprocess_runner``.
"""

import multiprocessing as mp
from multiprocessing.connection import wait

from onnx.backend.test.runner import BackendIsNotSupposedToImplementIt


class WorkerError(Exception):
    """Raised inside a worker to skip the test with the given message."""


def _worker_entry(target, args, conn):
    """Call target in the worker and send its result or skip reason to the parent."""
    try:
        conn.send(("ok", target(*args)))
    except WorkerError as e:
        conn.send(("error", str(e)))
    finally:
        conn.close()


def _read_result(reader):
    """Receive the worker's result, or None if it exited without sending all of it."""
    try:
        return reader.recv()
    except (EOFError, OSError):
        return None


def _stop_worker(process, finished):
    """Reap the worker, escalating to SIGTERM and then SIGKILL if it does not exit."""
    if finished:
        process.join(timeout=5)  # let the worker clean up and exit on its own
    if process.is_alive():
        process.terminate()
        process.join(timeout=5)
        if process.is_alive():
            process.kill()
            process.join()


def run_in_subprocess(target, args, *, timeout, name):
    """Return ``target(*args)`` evaluated in a spawned worker process.

    ``target`` must be a module-level function so it can be pickled. It returns
    the backend outputs, or raises ``WorkerError`` to skip the test. A timeout,
    a crash and a ``WorkerError`` all raise ``BackendIsNotSupposedToImplementIt``
    in the parent, with ``name`` identifying the backend in the message.
    """
    ctx = mp.get_context("spawn")
    reader, writer = ctx.Pipe(duplex=False)
    process = ctx.Process(target=_worker_entry, args=(target, args, writer))
    process.start()
    # With the parent's write end closed, a dead worker shows up as EOF on the
    # reader, and reading before joining keeps a large result from deadlocking.
    writer.close()
    ready = wait([reader, process.sentinel], timeout=timeout)
    outcome = _read_result(reader) if ready else None
    reader.close()
    _stop_worker(process, finished=bool(ready))
    if not ready:
        raise BackendIsNotSupposedToImplementIt(f"{name} process timed out")
    if outcome is None:
        raise BackendIsNotSupposedToImplementIt(
            f"{name} process crashed (exit code {process.exitcode})"
        )
    status, result = outcome
    if status == "error":
        raise BackendIsNotSupposedToImplementIt(result)
    return result
