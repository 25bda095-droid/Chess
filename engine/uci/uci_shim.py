import sys
import random

def main():
    while True:
        try:
            line = sys.stdin.readline()
        except EOFError:
            break
        
        if not line:
            break
            
        command = line.strip()
        if not command:
            continue
            
        parts = command.split()
        cmd = parts[0]
        
        if cmd == "uci":
            print("id name BasicUCI")
            print("id author Antigravity")
            print("uciok")
        elif cmd == "isready":
            print("readyok")
        elif cmd == "ucinewgame":
            pass
        elif cmd == "position":
            pass
        elif cmd == "go":
            # For now, just return a hardcoded or random move
            moves = ["e2e4", "d2d4", "g1f3", "b1c3"]
            move = random.choice(moves)
            print(f"bestmove {move}")
        elif cmd == "quit":
            break
            
        sys.stdout.flush()

if __name__ == "__main__":
    main()
