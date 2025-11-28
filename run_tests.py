#!/usr/bin/env python3
"""
Test runner for Mergen chess engine.

This script runs all test suites and provides a summary of results.
"""

import sys
import unittest
from pathlib import Path

# Add parent directory to path to import Source modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_move_generation import TestMoveGeneration, TestPerftPositions
from tests.test_evaluation import TestEvaluation, TestPieceValues
from tests.test_tactics import (TestMateInOne, TestMateInTwo, TestTacticalMotifs,
                                 TestEndgameKnowledge, TestAvoidBlunders)
from tests.test_opening_book import TestOpeningBook, TestOpeningBookManipulation
from tests.test_pgn import TestPGNSaveLoad, TestFENSaveLoad, TestPGNGameResults
from tests.test_parallel_search import TestParallelSearch
from tests.test_time_management import TestTimeManagement


def run_test_suite(verbosity=2):
    """
    Run all test suites.
    
    Args:
        verbosity: Level of output detail (0=minimal, 1=normal, 2=verbose)
    
    Returns:
        TestResult object
    """
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        # Move generation tests
        TestMoveGeneration,
        TestPerftPositions,
        TestParallelSearch,
        TestTimeManagement,
        
        # Evaluation tests
        TestEvaluation,
        TestPieceValues,
        
        # Tactical tests
        TestMateInOne,
        TestMateInTwo,
        TestTacticalMotifs,
        TestEndgameKnowledge,
        TestAvoidBlunders,
        
        # Opening book tests
        TestOpeningBook,
        TestOpeningBookManipulation,
        
        # PGN tests
        TestPGNSaveLoad,
        TestFENSaveLoad,
        TestPGNGameResults,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result


def run_specific_category(category, verbosity=2):
    """
    Run tests from a specific category.
    
    Args:
        category: One of 'moves', 'eval', 'tactics', 'book', 'pgn'
        verbosity: Level of output detail
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    category_map = {
        'moves': [TestMoveGeneration, TestPerftPositions],
        'parallel': [TestParallelSearch],
        'time': [TestTimeManagement],
        'eval': [TestEvaluation, TestPieceValues],
        'tactics': [TestMateInOne, TestMateInTwo, TestTacticalMotifs,
                   TestEndgameKnowledge, TestAvoidBlunders],
        'book': [TestOpeningBook, TestOpeningBookManipulation],
        'pgn': [TestPGNSaveLoad, TestFENSaveLoad, TestPGNGameResults],
    }
    
    if category not in category_map:
        print(f"Unknown category: {category}")
        print(f"Available categories: {', '.join(category_map.keys())}")
        return None
    
    for test_class in category_map[category]:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Mergen chess engine tests')
    parser.add_argument('category', nargs='?', default='all',
                       help='Test category to run (all, moves, parallel, time, eval, tactics, book, pgn)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Minimal output')
    
    args = parser.parse_args()
    
    # Determine verbosity
    verbosity = 2  # Default verbose
    if args.quiet:
        verbosity = 0
    elif not args.verbose:
        verbosity = 1
    
    # Run tests
    print(f"Running Mergen chess engine tests...")
    print(f"{'='*70}\n")
    
    if args.category == 'all':
        result = run_test_suite(verbosity=verbosity)
    else:
        result = run_specific_category(args.category, verbosity=verbosity)
        if result is None:
            return 1
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
