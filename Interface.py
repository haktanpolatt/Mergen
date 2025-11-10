###############################
#                             #
#   Created on June 7, 2025   #
#                             #
###############################

import ctypes
import os
import platform
import subprocess
import sys

# -------------------------
# Settings
# -------------------------

SRC_DIR = os.path.join("Source", "C")  # Source directory containing C files
system_name = platform.system()

# Name of the shared library based on the operating system
# Windows uses .dll, Linux uses .so, and macOS uses .dylib
if system_name == "Windows":
    lib_name = "Engine.dll"
elif system_name == "Linux":
    lib_name = "Engine.so"
elif system_name == "Darwin": # macOS
    lib_name = "Engine.dylib"
else:
    raise OSError(f"Unsupported OS: {system_name}")

lib_path = os.path.abspath(os.path.join(SRC_DIR, lib_name))

# -------------------------
# Check if the library exists, if not compile it
# -------------------------

if not os.path.exists(lib_path):
    print(f"[INFO] {lib_name} is not found. Compiling...")

    # List of C source files to compile
    c_files = [
        "Engine.c", "Board.c", "MoveGen.c", "Evaluate.c",
        "Minimax.c", "Move.c", "Rules.c", "Zobrist.c",
        "TT.c", "Ordering.c", "KillerMoves.c", "ParallelSearch.c"
    ]
    c_files = [os.path.join(SRC_DIR, f) for f in c_files]

    # Compilation command
    if system_name == "Windows":
        cmd = ["gcc", "-O3", "-shared", "-o", lib_path] + c_files + ["-Wno-stringop-overflow"]
    else:
        cmd = ["gcc", "-O3", "-shared", "-fPIC", "-o", lib_path] + c_files + ["-Wno-stringop-overflow"]

    # Run the compilation command
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit("[ERROR] Compilation failed!")

print(f"[OK] {lib_name} is found, loading...")

# -------------------------
# Load the shared library
# -------------------------

lib = ctypes.CDLL(lib_path)

# -------------------------
# Function Prototypes
# -------------------------

# get_best_move_from_c
lib.find_best_move_from_fen.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.find_best_move_from_fen.restype = ctypes.c_char_p

def get_best_move_from_c(fen: str, depth: int = 4) -> str:
    move = lib.find_best_move_from_fen(fen.encode(), depth)
    return move.decode()

# get_eval_from_c
lib.evaluate_fen.argtypes = [ctypes.c_char_p]
lib.evaluate_fen.restype = ctypes.c_float

def get_eval_from_c(fen: str) -> float:
    return lib.evaluate_fen(fen.encode())

# get_search_info_from_c
lib.get_search_info.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.get_search_info.restype = ctypes.c_char_p

def get_search_info_from_c(fen: str, depth: int = 4) -> str:
    """
    Get detailed search information including depth, evaluation, and principal variation.
    Returns string in format: "depth score pv_move"
    """
    info = lib.get_search_info(fen.encode(), depth)
    return info.decode()

# find_best_move_timed_from_c
lib.find_best_move_timed.argtypes = [ctypes.c_char_p, ctypes.c_float]
lib.find_best_move_timed.restype = ctypes.c_char_p

def find_best_move_timed_from_c(fen: str, max_time_ms: float) -> tuple:
    """
    Find best move with time management.
    Searches as deep as possible within time limit using iterative deepening.
    
    Args:
        fen: Position in FEN format
        max_time_ms: Maximum time in milliseconds
        
    Returns:
        Tuple of (move_uci, depth_reached, time_spent_ms)
    """
    result = lib.find_best_move_timed(fen.encode(), max_time_ms)
    result_str = result.decode()
    parts = result_str.split()
    if len(parts) >= 3:
        return (parts[0], int(parts[1]), float(parts[2]))
    return (parts[0], 0, 0.0)

# get_cpu_cores
lib.get_cpu_cores.argtypes = []
lib.get_cpu_cores.restype = ctypes.c_int

def get_cpu_cores() -> int:
    """
    Get the number of available CPU cores.
    
    Returns:
        Number of CPU cores
    """
    return lib.get_cpu_cores()

# find_best_move_parallel_from_c
lib.find_best_move_parallel_from_fen.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
lib.find_best_move_parallel_from_fen.restype = ctypes.c_char_p

def find_best_move_parallel_from_c(fen: str, depth: int, num_threads: int) -> str:
    """
    Find best move using parallel search (Lazy SMP).
    Uses multiple threads to speed up search.
    
    Args:
        fen: Position in FEN format
        depth: Search depth
        num_threads: Number of threads to use
        
    Returns:
        Best move in UCI format
    """
    move = lib.find_best_move_parallel_from_fen(fen.encode(), depth, num_threads)
    return move.decode()

# find_best_move_parallel_timed_from_c
lib.find_best_move_parallel_timed_from_fen.argtypes = [ctypes.c_char_p, ctypes.c_float, ctypes.c_int]
lib.find_best_move_parallel_timed_from_fen.restype = ctypes.c_char_p

def find_best_move_parallel_timed_from_c(fen: str, max_time_ms: float, num_threads: int) -> tuple:
    """
    Find best move using parallel search with time management.
    Uses multiple threads and searches as deep as possible within time limit.
    
    Args:
        fen: Position in FEN format
        max_time_ms: Maximum time in milliseconds
        num_threads: Number of threads to use
        
    Returns:
        Tuple of (move_uci, depth_reached, time_spent_ms)
    """
    result = lib.find_best_move_parallel_timed_from_fen(fen.encode(), max_time_ms, num_threads)
    result_str = result.decode()
    parts = result_str.split()
    if len(parts) >= 3:
        return (parts[0], int(parts[1]), float(parts[2]))
    return (parts[0], 0, 0.0)

