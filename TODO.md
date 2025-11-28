# TODO

- Fix multi-threaded search performance regression at depth 4+ in `Source/C/ParallelSearch.*`; add a benchmark/regression test so the fast path is safe to enable.
- Align `test_fast.py` description with actual settings (currently runs depth 2); either bump the depth or update the text so the quick self-play check is accurate.
- Wire UCI `Hash`/`Threads` options through to the C engine (hash size currently a placeholder); document effective limits once implemented.
- Add automated test invocation (CI or pre-commit) for `run_tests.py` to keep the 50+ unit tests green across changes.
- Validate opening book stats (README says 108 positions/186 moves); add a small test to confirm `Data/opening_book.json` counts and keep docs in sync.
- Expand time-management coverage with unit tests for each control (bullet, blitz, rapid, classical, infinite) and emergency-mode behavior.
