#!/usr/bin/env python3
"""Test to measure thread creation overhead"""

import time
import ctypes
import os

# Load engine
lib_path = os.path.join(os.path.dirname(__file__), "Source", "C", "Engine.so")
engine = ctypes.CDLL(lib_path)

# Configure functions
engine.find_best_move_parallel.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
engine.find_best_move_parallel.restype = ctypes.c_char_p

engine.find_best_move_from_fen.argtypes = [ctypes.c_char_p, ctypes.c_int]
engine.find_best_move_from_fen.restype = ctypes.c_char_p

# Simple position
fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

print("Testing thread overhead...")
print("=" * 50)

# Test depth 1-4 with single thread
print("\nSingle-threaded (baseline):")
for depth in [1, 2, 3, 4]:
    start = time.time()
    result = engine.find_best_move_from_fen(fen.encode('utf-8'), depth)
    elapsed = time.time() - start
    move = result.decode('utf-8')
    print(f"  Depth {depth}: {elapsed:.4f}s - Move: {move}")

# Test depth 1-4 with parallel (1 thread)
print("\nParallel with 1 thread:")
for depth in [1, 2, 3, 4]:
    start = time.time()
    result = engine.find_best_move_parallel(fen.encode('utf-8'), depth, 1)
    elapsed = time.time() - start
    move = result.decode('utf-8')
    print(f"  Depth {depth}: {elapsed:.4f}s - Move: {move}")

# Test depth 3 with multiple threads
print("\nDepth 3 with varying threads:")
for threads in [1, 2, 4, 8]:
    start = time.time()
    result = engine.find_best_move_parallel(fen.encode('utf-8'), 3, threads)
    elapsed = time.time() - start
    move = result.decode('utf-8')
    print(f"  {threads} thread(s): {elapsed:.4f}s - Move: {move}")
    
# Test depth 4 with varying threads (this is where bug appears)
print("\nDepth 4 with varying threads (BUGGY):")
for threads in [1, 2]:
    start = time.time()
    result = engine.find_best_move_parallel(fen.encode('utf-8'), 4, threads)
    elapsed = time.time() - start
    move = result.decode('utf-8')
    print(f"  {threads} thread(s): {elapsed:.4f}s - Move: {move}")
    if elapsed > 5:
        print("  ⚠️ SLOWDOWN DETECTED! Stopping test.")
        break
