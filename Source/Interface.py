###############################
#                             #
#   Created on June 7, 2025   #
#                             #
###############################

import ctypes
import os

# Path of compiled shared library file (.so for Linux, .dll for Windows)
lib = ctypes.CDLL(os.path.abspath("Source/C/Engine.dll"))

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


