#!/usr/bin/env python3
"""
Quick benchmark to compare single-thread vs parallel search timing.
Targets depth 3 to avoid long runs; use for spotting regressions in Lazy SMP.
"""

import time
from typing import List, Dict

from Interface import get_best_move_from_c, find_best_move_parallel_from_c


TEST_POSITIONS: List[Dict[str, str]] = [
    {
        "name": "Starting Position",
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    },
    {
        "name": "Italian Game",
        "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
    },
    {
        "name": "Tactical Middlegame",
        "fen": "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 5",
    },
]


def time_call(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return result, elapsed


def main():
    depth = 3
    threads = 2

    print("=== Parallel benchmark (depth={depth}, threads={threads}) ===".format(
        depth=depth, threads=threads
    ))

    for pos in TEST_POSITIONS:
        fen = pos["fen"]
        name = pos["name"]
        print(f"\n{name}")
        _, t_single = time_call(get_best_move_from_c, fen, depth)
        _, t_parallel = time_call(find_best_move_parallel_from_c, fen, depth, threads)

        speedup = t_single / t_parallel if t_parallel > 0 else 0
        print(f"  single-thread:  {t_single:6.3f}s")
        print(f"  {threads} threads: {t_parallel:6.3f}s")
        print(f"  speedup:       {speedup:6.2f}x")

        if t_parallel > t_single:
            print("  [warn] parallel slower than single-thread here (regression suspect)")


if __name__ == "__main__":
    main()
