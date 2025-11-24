###############################
#                             #
#   Created on Nov 24, 2025   #
#                             #
###############################

#!/usr/bin/env python3
"""
Mergen Chess Engine - UCI Mode Launcher

This script launches Mergen in UCI (Universal Chess Interface) mode,
making it compatible with chess GUIs like Arena, ChessBase, Cute Chess, etc.

Usage:
    python uci_launcher.py

Or configure your chess GUI to run this script as the engine executable.
"""

if __name__ == "__main__":
    from uci import main
    main()
