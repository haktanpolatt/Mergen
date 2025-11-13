#!/usr/bin/env python3
"""Final verification test"""

import time
import ctypes
import os

lib_path = os.path.join(os.path.dirname(__file__), "Source", "C", "Engine.so")
engine = ctypes.CDLL(lib_path)

engine.find_best_move_from_fen.argtypes = [ctypes.c_char_p, ctypes.c_int]
engine.find_best_move_from_fen.restype = ctypes.c_char_p

engine.find_best_move_parallel.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
engine.find_best_move_parallel.restype = ctypes.c_char_p

# Position after e2e4 d7d5 e4e5
fen = "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2"

print("Comparing single vs multi-threaded at depth 4:")
print("=" * 60)

print("\n1. Single-threaded baseline:")
start = time.time()
result = engine.find_best_move_from_fen(fen.encode('utf-8'), 4)
elapsed1 = time.time() - start
move1 = result.decode('utf-8')
print(f"   Time: {elapsed1:.2f}s, Move: {move1}")

print("\n2. Parallel with 1 thread (should be similar):")
start = time.time()
result = engine.find_best_move_parallel(fen.encode('utf-8'), 4, 1)
elapsed2 = time.time() - start
move2 = result.decode('utf-8')
print(f"   Time: {elapsed2:.2f}s, Move: {move2}")

print("\n3. Parallel with 2 threads (testing speedup/slowdown):")
start = time.time()
result = engine.find_best_move_parallel(fen.encode('utf-8'), 4, 2)
elapsed3 = time.time() - start
move3 = result.decode('utf-8')
print(f"   Time: {elapsed3:.2f}s, Move: {move3}")

print("\n" + "=" * 60)
print(f"Speedup with 2 threads: {elapsed1/elapsed3:.2f}x")
if elapsed3 > elapsed1:
    print(f"⚠️  WARNING: 2 threads is {elapsed3/elapsed1:.2f}x SLOWER!")
