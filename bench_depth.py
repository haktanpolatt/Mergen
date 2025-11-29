#!/usr/bin/env python3
"""
Depth-based benchmark for parallel search.
Compares single-thread vs multi-thread wall-clock at fixed depth.
Use small depths to avoid runaway runtimes.
"""

import time
from typing import List, Dict

from Interface import (
    get_best_move_from_c,
    find_best_move_parallel_from_c,
    find_best_move_parallel_timed_from_c,
)

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


def bench(depth: int, threads: int, max_seconds: float = 10.0):
    print(f"=== Depth bench: depth={depth}, threads={threads} ===")
    for pos in TEST_POSITIONS:
        fen = pos["fen"]
        name = pos["name"]
        start = time.perf_counter()
        if threads == 1:
            move = get_best_move_from_c(fen, depth)
            elapsed = time.perf_counter() - start
            print(f"{name:<22} {elapsed:6.3f}s  move {move}")
        else:
            move = find_best_move_parallel_from_c(fen, depth, threads)
            elapsed = time.perf_counter() - start
            print(f"{name:<22} {elapsed:6.3f}s  move {move}")
        if elapsed > max_seconds:
            print("  [warn] exceeded max_seconds cap, stopping further benches")
            break
    print()


def timed_bench(max_ms: int, threads: int):
    print(f"=== Timed bench: {max_ms} ms, threads={threads} ===")
    for pos in TEST_POSITIONS:
        fen = pos["fen"]
        name = pos["name"]
        start = time.perf_counter()
        move, depth, spent_ms, nodes = find_best_move_parallel_timed_from_c(fen, max_ms, threads)
        elapsed = time.perf_counter() - start
        print(f"{name:<22} {elapsed:6.3f}s  move {move} depth {depth} engine {spent_ms/1000:4.2f}s nodes {nodes}")
    print()


if __name__ == "__main__":
    for depth in [3, 4]:
        bench(depth, 1)
        for t in [2, 3, 4]:
            bench(depth, t)
    # Timed sanity: 2s cap
    for t in [1, 2, 3, 4]:
        timed_bench(2000, t)
