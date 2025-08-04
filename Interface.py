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
        "TT.c", "Ordering.c", "KillerMoves.c"
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

