import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mistake_tracker import MistakeTracker

def run_analysis():
    tracker = MistakeTracker(recurring_threshold=3)
    
    # Simulate user game mistakes across recent games
    mock_mistakes = [
        "hanging_piece", "missed_mate", "blunder", 
        "hanging_piece", "forked", "hanging_piece",
        "missed_mate", "pinned_piece", "hanging_piece",
        "missed_mate", "blunder"
    ]
    
    for mistake in mock_mistakes:
        tracker.record_mistake(mistake)
        
    profile = tracker.get_profile()
    
    report = "User Mistake Tracking Analysis Report\n"
    report += "=====================================\n"
    report += f"Total Mistakes Recorded: {profile['total_mistakes']}\n\n"
    report += "Mistake Frequencies:\n"
    for mistake, count in sorted(profile['mistake_frequencies'].items(), key=lambda x: x[1], reverse=True):
        report += f"  - {mistake}: {count}\n"
        
    report += "\nRecurring Vulnerabilities (Threshold >= 3):\n"
    if profile['recurring_vulnerabilities']:
        for vuln in profile['recurring_vulnerabilities']:
            report += f"  - [ALERT] {vuln}\n"
    else:
        report += "  - None\n"
        
    print(report)

if __name__ == "__main__":
    run_analysis()
