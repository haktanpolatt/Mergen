#!/usr/bin/env python3
"""Quick test to measure actual search speed"""

import time
import ctypes
import os

# Load engine
lib_path = os.path.join(os.path.dirname(__file__), "Source", "C", "Engine.so")
engine = ctypes.CDLL(lib_path)

# Configure function
engine.find_best_move_parallel.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
engine.find_best_move_parallel.restype = ctypes.c_char_p

# Test position after e4 d5 e5
fen = "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2"

print("Testing search speed...")
print(f"Position: {fen}")
print(f"Searching to depth 4 with 8 threads...")

start = time.time()
result = engine.find_best_move_parallel(fen.encode('utf-8'), 4, 8)
elapsed = time.time() - start

move = result.decode('utf-8')
print(f"\nBest move: {move}")
print(f"Time taken: {elapsed:.2f} seconds")

# Now test with single thread
print(f"\nSearching to depth 4 with 1 thread...")
start = time.time()
result = engine.find_best_move_parallel(fen.encode('utf-8'), 4, 1)
elapsed = time.time() - start

move = result.decode('utf-8')
print(f"Best move: {move}")
print(f"Time taken: {elapsed:.2f} seconds")

# Test depth 3 for comparison
print(f"\nSearching to depth 3 with 8 threads...")
start = time.time()
result = engine.find_best_move_parallel(fen.encode('utf-8'), 3, 8)
elapsed = time.time() - start

move = result.decode('utf-8')
print(f"Best move: {move}")
print(f"Time taken: {elapsed:.2f} seconds")
