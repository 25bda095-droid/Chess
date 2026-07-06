#!/usr/bin/env python3
import subprocess
import re
import argparse
import sys
import math

def calculate_elo_diff(wins, draws, losses):
    total = wins + draws + losses
    if total == 0:
        return 0.0, 0.0

    score = (wins + draws * 0.5) / total
    if score == 0:
        score = 0.001
    elif score == 1:
        score = 0.999
    
    elo_diff = -400 * math.log10(1 / score - 1)
    
    # Simple error margin estimation approximation
    dev = math.sqrt((score * (1 - score)) / total)
    error_margin = 400 * math.log10(1 / (max(0.001, score - dev)) - 1) - elo_diff if score - dev > 0 else 0
    return elo_diff, abs(error_margin)

def main():
    parser = argparse.ArgumentParser(description="Run matches using cutechess-cli and calculate Elo.")
    parser.add_argument("--engine1", required=True, help="Path to test engine or cutechess engine config")
    parser.add_argument("--engine2", required=True, help="Path to baseline engine or cutechess engine config")
    parser.add_argument("--rounds", type=int, default=10, help="Number of rounds to play")
    parser.add_argument("--tc", default="10+0.1", help="Time control (e.g. 10+0.1)")
    parser.add_argument("--concurrency", type=int, default=1, help="Number of concurrent games")
    parser.add_argument("--cutechess", default="cutechess-cli", help="Path to cutechess-cli executable")
    
    args = parser.parse_args()
    
    cmd = [
        args.cutechess,
        "-engine", f"cmd={args.engine1}", "name=TestEngine",
        "-engine", f"cmd={args.engine2}", "name=BaselineEngine",
        "-each", "proto=uci", f"tc={args.tc}",
        "-rounds", str(args.rounds),
        "-concurrency", str(args.concurrency),
        "-recover"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    except FileNotFoundError:
        print(f"Error: {args.cutechess} not found. Please install cutechess-cli or provide the correct path.", file=sys.stderr)
        sys.exit(1)

    wins, draws, losses = 0, 0, 0
    
    # Sample Output to parse:
    # Score of TestEngine vs BaselineEngine: 5 - 3 - 2  [0.600] 10
    score_pattern = re.compile(r"Score of TestEngine vs BaselineEngine:\s+(\d+)\s+-\s+(\d+)\s+-\s+(\d+)")

    for line in iter(process.stdout.readline, ""):
        print(line, end="")
        match = score_pattern.search(line)
        if match:
            wins = int(match.group(1))
            losses = int(match.group(2))
            draws = int(match.group(3))

    process.wait()
    
    if process.returncode != 0:
        print(f"Warning: cutechess-cli exited with code {process.returncode}", file=sys.stderr)
        
    elo_diff, error = calculate_elo_diff(wins, draws, losses)
    
    print("\n" + "="*40)
    print("Match Results")
    print("="*40)
    print(f"Wins:   {wins}")
    print(f"Draws:  {draws}")
    print(f"Losses: {losses}")
    print(f"Total:  {wins + draws + losses}")
    print(f"Elo diff: {elo_diff:.2f} +/- {error:.2f}")

if __name__ == "__main__":
    main()
