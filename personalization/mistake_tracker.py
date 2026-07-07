from collections import defaultdict
from typing import List, Dict, Any

class MistakeTracker:
    """
    Tracks user mistakes in chess games and maintains a profile of recurring vulnerabilities.
    """
    def __init__(self, recurring_threshold: int = 3):
        # A dictionary mapping mistake types to their frequency
        self.mistakes_count: Dict[str, int] = defaultdict(int)
        # Threshold for considering a mistake a "recurring vulnerability"
        self.recurring_threshold = recurring_threshold
        # History of all recorded mistakes
        self.history: List[Dict[str, str]] = []

    def record_mistake(self, mistake_type: str, fen: str = None) -> None:
        """
        Record a mistake made by the user.
        Example mistake types: "hanging_piece", "missed_mate", "blunder", "forked"
        """
        self.mistakes_count[mistake_type] += 1
        self.history.append({"mistake_type": mistake_type, "fen": fen})

    def get_recurring_vulnerabilities(self) -> List[str]:
        """
        Returns a list of mistake types that meet or exceed the recurring threshold.
        """
        return [
            mistake for mistake, count in self.mistakes_count.items()
            if count >= self.recurring_threshold
        ]

    def get_profile(self) -> Dict[str, Any]:
        """
        Returns the user's vulnerability profile.
        """
        return {
            "total_mistakes": len(self.history),
            "mistake_frequencies": dict(self.mistakes_count),
            "recurring_vulnerabilities": self.get_recurring_vulnerabilities()
        }
