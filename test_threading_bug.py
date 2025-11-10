#!/usr/bin/env python3
"""Test to isolate the threading bug"""

import time
import ctypes
import os

# Load engine
lib_path = os.path.join(os.path.dirname(__file__), "Engine.so")
engine = ctypes.CDLL(lib_path)

# Configure function
engine.find_best_move_parallel.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
engine.find_best_move_parallel.restype = ctypes.c_char_p

# Test position after e4 d5 e5
fen = "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2"

print("Testing different thread counts at depth 4...")

for threads in [1, 2, 4, 8]:
    print(f"\nThreads: {threads}")
    start = time.time()
    result = engine.find_best_move_parallel(fen.encode('utf-8'), 4, threads)
    elapsed = time.time() - start
    move = result.decode('utf-8')
    print(f"  Move: {move}, Time: {elapsed:.2f}s")
    
    if elapsed > 10:
        print("  ⚠️  HANGS WITH THIS THREAD COUNT!")
        break
