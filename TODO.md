# TODO

- Fix multi-threaded search performance regression at depth 4+ in `Source/C/ParallelSearch.*`; add a benchmark/regression test so the fast path is safe to enable. (Added basic legality tests; performance profiling still needed.)
- Wire UCI `Hash`/`Threads` options through to the C engine (hash size currently a placeholder); document effective limits once implemented.
- Add automated test invocation (CI or pre-commit) for `run_tests.py` to keep the 50+ unit tests green across changes. (GitHub Actions workflow added; enable in repo.)
- Expand time-management coverage with unit tests for each control (bullet, blitz, rapid, classical, infinite) and emergency-mode behavior.
