###############################
#                             #
#   Created on May 26, 2025   #
#                             #
###############################

from rich.console import Console

console = Console()

def format_time(seconds):
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

def print_status(white_score, black_score, white_time, black_time):
    console.print(f"[green]White Score:[/] {white_score:.2f}   [red]Black Score:[/] {black_score:.2f}")
    console.print(f"[green]White Time:[/] {format_time(white_time)}   [red]Black Time:[/] {format_time(black_time)}")
