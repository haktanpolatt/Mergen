###############################
#                             #
#   Created on June 7, 2025   #
#                             #
###############################

import ctypes
import os

# Derlenmiş shared library yolunu belirt (Linux için .so, Windows için .dll)
lib = ctypes.CDLL(os.path.abspath("Source/C/Engine.dll"))

# C fonksiyonunu tanımla
lib.find_best_move_from_fen.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.find_best_move_from_fen.restype = ctypes.c_char_p

def get_best_move_from_c(fen: str, depth: int = 4) -> str:
    move = lib.find_best_move_from_fen(fen.encode(), depth)
    return move.decode()
