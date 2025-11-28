#!/usr/bin/env python3
"""
Performance profiling for Mergen chess engine
Tests search speed at various depths and positions
"""
import sys
import time
sys.path.append('Source')
from Interface import get_best_move_from_c

# Test positions with varying complexity
test_positions = [
    {
        "name": "Starting Position",
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "complexity": "High branching factor (20 legal moves)"
    },
    {
        "name": "Italian Opening",
        "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
        "complexity": "Mid-game, ~30 legal moves"
    },
    {
        "name": "Endgame Position",
        "fen": "8/5k2/3p4/1p1Pp2p/pP2Pp1P/P4P1K/8/8 b - - 99 50",
        "complexity": "Endgame, ~10 legal moves"
    },
    {
        "name": "Tactical Position",
        "fen": "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 5",
        "complexity": "Tactical, ~35 legal moves"
    },
]

print("=" * 70)
print("MERGEN CHESS ENGINE - PERFORMANCE ANALYSIS")
print("=" * 70)
print()

# Test each position at increasing depths
for pos in test_positions:
    print(f"\n{'='*70}")
    print(f"Position: {pos['name']}")
    print(f"FEN: {pos['fen']}")
    print(f"Complexity: {pos['complexity']}")
    print(f"{'='*70}")
    
    for depth in range(3, 7):  # Test depths 3-6
        print(f"\nDepth {depth}...", end=" ", flush=True)
        
        start = time.time()
        try:
            move = get_best_move_from_c(pos['fen'], depth)
            elapsed = time.time() - start
            
            # Calculate nodes per second (rough estimate)
            # Assuming exponential growth: ~35 moves avg, ~35^depth nodes
            estimated_nodes = 35 ** depth
            nps = estimated_nodes / elapsed if elapsed > 0 else 0
            
            print(f"✓ Move: {move:6s} | Time: {elapsed:6.3f}s | ~{nps/1000:.0f}k NPS")
            
            # Stop if search takes more than 20 seconds
            if elapsed > 20:
                print(f"  → Stopping tests for this position (depth {depth} took >20s)")
                break
                
        except KeyboardInterrupt:
            print("✗ Interrupted")
            break
        except Exception as e:
            print(f"✗ Error: {e}")
            break

print("\n" + "=" * 70)
print("PERFORMANCE SUMMARY")
print("=" * 70)
print("\nKey Observations:")
print("- Depth 3-4 should complete in under 2 seconds")
print("- Depth 5 complexity depends heavily on position")
print("- Endgame positions should be faster than opening positions")
print("- If depth 5 takes >15s on simple endgames, there's a bottleneck")
print("\nRecommendations will depend on the results above.")
print("=" * 70)
