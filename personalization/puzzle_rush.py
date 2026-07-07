import sys
import os
import random
from typing import List, Dict

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mistake_tracker import MistakeTracker

class PuzzleRushMode:
    """
    Puzzle Rush Mode extension.
    Takes blunder history from mistake_tracker and auto-generates tactical puzzles
    (e.g., FEN strings of the blunder positions) for the user to solve.
    """
    def __init__(self, tracker: MistakeTracker):
        self.tracker = tracker
        
        # Fallback database if no FEN is provided in the history
        self.fallback_fens = {
            "hanging_piece": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
            "missed_mate": "3r2k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1",
            "blunder": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "forked": "4k3/8/8/8/8/8/4N3/4K3 w - - 0 1",
            "pinned_piece": "4k3/8/8/4r3/8/8/4R3/4K3 w - - 0 1"
        }

    def generate_puzzles(self) -> List[Dict[str, str]]:
        """
        Extracts positions from the mistake history to create puzzles.
        If a mistake lacks a specific FEN, it falls back to a template FEN for that mistake type.
        """
        puzzles = []
        for entry in self.tracker.history:
            mistake_type = entry.get("mistake_type", "blunder")
            fen = entry.get("fen")
            
            if not fen:
                fen = self.fallback_fens.get(mistake_type, self.fallback_fens["blunder"])
                
            puzzles.append({
                "mistake_type": mistake_type,
                "fen": fen
            })
            
        return puzzles

    def start_rush(self):
        """
        Simulates the puzzle rush.
        """
        print("=== PUZZLE RUSH MODE ===")
        puzzles = self.generate_puzzles()
        
        if not puzzles:
            print("No mistakes found in history to generate puzzles.")
            return
            
        print(f"Generated {len(puzzles)} puzzles based on your blunder history!\n")
        for i, puzzle in enumerate(puzzles, 1):
            print(f"Puzzle #{i} - Theme: {puzzle['mistake_type'].replace('_', ' ').title()}")
            print(f"Solve this position (FEN): {puzzle['fen']}")
            print("-" * 30)

if __name__ == "__main__":
    tracker = MistakeTracker(recurring_threshold=2)
    # Recording mistakes with and without explicit FEN strings
    tracker.record_mistake("hanging_piece", "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3")
    tracker.record_mistake("missed_mate") # Will use fallback
    tracker.record_mistake("blunder", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    
    rush = PuzzleRushMode(tracker)
    rush.start_rush()
