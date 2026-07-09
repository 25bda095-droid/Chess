import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from engine.selfplay.loop import NNUEMCTSAgent
from engine.core.board import Board

def main():
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nnue_base_model_final.pth'))
    agent = NNUEMCTSAgent(model_path=model_path, use_tablebase=True)
    board = Board()

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
            board.reset()
        elif cmd == "position":
            if "startpos" in parts:
                board.reset()
                if "moves" in parts:
                    moves_idx = parts.index("moves")
                    for m in parts[moves_idx+1:]:
                        board.push_uci(m)
            elif "fen" in parts:
                fen_idx = parts.index("fen")
                moves_idx = parts.index("moves") if "moves" in parts else len(parts)
                fen = " ".join(parts[fen_idx+1:moves_idx])
                board.set_fen(fen)
                if moves_idx < len(parts):
                    for m in parts[moves_idx+1:]:
                        board.push_uci(m)
        elif cmd == "go":
            policy_probs = agent.search_and_get_policy(board)
            if policy_probs:
                move = max(policy_probs, key=policy_probs.get)
            else:
                moves = list(board.generate_legal_moves())
                move = moves[0].uci() if moves else "0000"
            print(f"bestmove {move}")
        elif cmd == "quit":
            break
            
        sys.stdout.flush()

if __name__ == "__main__":
    main()
