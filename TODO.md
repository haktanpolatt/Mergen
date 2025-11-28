# TODO

- Fix multi-threaded search performance regression at depth 4+ in `Source/C/ParallelSearch.*`; add a benchmark/regression test so the fast path is safe to enable. (Bench shows ~1x at depth-4 timed 2s cap; investigate workload splitting/ordering.)
- Wire UCI `Hash`/`Threads` options through to the C engine (hash size now configurable via `setoption Hash` → TT resize; document effective limits once validated.)
- Add automated test invocation (CI or pre-commit) for `run_tests.py` to keep the 50+ unit tests green across changes. (GitHub Actions workflow added; enable in repo.)
- Expand time-management coverage with unit tests for each control (bullet, blitz, rapid, classical, infinite) and emergency-mode behavior. (Control-scaling tests added; could extend to increment-heavy scenarios.)
- Investigate timed search overrun: `find_best_move_timed_from_c` and parallel variant exceed `max_time_ms` caps (e.g., benchmark shows 36s on 2000ms cap). Add guardrails or fix C timer logic. (Fixed with monotonic timers + in-search time checks; benchmark respects 2s cap but parallel still offers minimal speedup.)
